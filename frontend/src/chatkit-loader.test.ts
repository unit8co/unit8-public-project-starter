import { describe, expect, it } from "vitest";

import indexHtml from "../index.html?raw";

describe("ChatKit loader", () => {
  it("keeps the ChatKit web component loader in the frontend template", () => {
    expect(indexHtml).toContain(
      "https://cdn.platform.openai.com/deployments/chatkit/chatkit.js",
    );
  });
});
