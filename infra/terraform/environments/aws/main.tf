data "aws_availability_zones" "available" {}

locals {
  azs = slice(data.aws_availability_zones.available.names, 0, 2)
}

module "app_service" {
  source = "../../modules/app_service"

  application_name = var.application_name
  environment      = var.environment
  location         = var.region
  container_image  = var.container_image
  container_port   = var.container_port
  env_vars         = var.env_vars
  secret_names     = var.secret_names
  tags             = var.tags
}

resource "aws_vpc" "this" {
  cidr_block           = "10.42.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(module.app_service.labels, { Name = "${module.app_service.name_prefix}-vpc" })
}

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id

  tags = merge(module.app_service.labels, { Name = "${module.app_service.name_prefix}-igw" })
}

resource "aws_subnet" "public" {
  for_each = {
    for index, az in local.azs :
    az => {
      cidr = cidrsubnet(aws_vpc.this.cidr_block, 8, index)
      az   = az
    }
  }

  vpc_id                  = aws_vpc.this.id
  cidr_block              = each.value.cidr
  availability_zone       = each.value.az
  map_public_ip_on_launch = true

  tags = merge(module.app_service.labels, { Name = "${module.app_service.name_prefix}-${each.key}" })
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.this.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.this.id
  }

  tags = merge(module.app_service.labels, { Name = "${module.app_service.name_prefix}-public-rt" })
}

resource "aws_route_table_association" "public" {
  for_each = aws_subnet.public

  subnet_id      = each.value.id
  route_table_id = aws_route_table.public.id
}

resource "aws_security_group" "alb" {
  name        = "${module.app_service.name_prefix}-alb"
  description = "ALB ingress"
  vpc_id      = aws_vpc.this.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(module.app_service.labels, { Name = "${module.app_service.name_prefix}-alb-sg" })
}

resource "aws_security_group" "service" {
  name        = "${module.app_service.name_prefix}-service"
  description = "ECS service ingress"
  vpc_id      = aws_vpc.this.id

  ingress {
    from_port       = module.app_service.container_port
    to_port         = module.app_service.container_port
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(module.app_service.labels, { Name = "${module.app_service.name_prefix}-service-sg" })
}

resource "aws_lb" "this" {
  name               = substr(replace(module.app_service.name_prefix, "/[^a-zA-Z0-9-]/", "-"), 0, 32)
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = [for subnet in aws_subnet.public : subnet.id]

  tags = merge(module.app_service.labels, { Name = "${module.app_service.name_prefix}-alb" })
}

resource "aws_lb_target_group" "this" {
  name        = substr(replace("${module.app_service.name_prefix}-tg", "/[^a-zA-Z0-9-]/", "-"), 0, 32)
  port        = module.app_service.container_port
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = aws_vpc.this.id

  health_check {
    path                = "/healthz"
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }

  tags = merge(module.app_service.labels, { Name = "${module.app_service.name_prefix}-tg" })
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.this.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.this.arn
  }
}

resource "aws_cloudwatch_log_group" "this" {
  name              = "/ecs/${module.app_service.name_prefix}"
  retention_in_days = 30
  tags              = module.app_service.labels
}

data "aws_iam_policy_document" "ecs_task_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "execution" {
  name               = "${module.app_service.name_prefix}-execution"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role.json
  tags               = module.app_service.labels
}

resource "aws_iam_role_policy_attachment" "execution" {
  role       = aws_iam_role.execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "task" {
  name               = "${module.app_service.name_prefix}-task"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role.json
  tags               = module.app_service.labels
}

resource "aws_ecs_cluster" "this" {
  name = module.app_service.name_prefix

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = module.app_service.labels
}

resource "aws_ecs_task_definition" "this" {
  family                   = module.app_service.name_prefix
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = tostring(var.cpu)
  memory                   = tostring(var.memory)
  execution_role_arn       = aws_iam_role.execution.arn
  task_role_arn            = aws_iam_role.task.arn

  container_definitions = jsonencode([
    {
      name      = "api"
      image     = module.app_service.container_image
      essential = true
      portMappings = [
        {
          containerPort = module.app_service.container_port
          hostPort      = module.app_service.container_port
          protocol      = "tcp"
        }
      ]
      environment = [
        for key, value in module.app_service.env_vars : {
          name  = key
          value = value
        }
      ]
      secrets = [
        for secret_name in module.app_service.secret_names : {
          name      = upper(replace(secret_name, "-", "_"))
          valueFrom = "arn:aws:secretsmanager:${var.region}:123456789012:secret:${secret_name}"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.this.name
          awslogs-region        = var.region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])

  tags = module.app_service.labels
}

resource "aws_ecs_service" "this" {
  name            = module.app_service.name_prefix
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.this.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    assign_public_ip = true
    security_groups  = [aws_security_group.service.id]
    subnets          = [for subnet in aws_subnet.public : subnet.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.this.arn
    container_name   = "api"
    container_port   = module.app_service.container_port
  }

  depends_on = [aws_lb_listener.http]

  tags = module.app_service.labels
}
