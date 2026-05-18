import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const chatKitMock = vi.hoisted(() => ({
  useChatKit: vi.fn(),
}));

vi.mock("@openai/chatkit-react", () => ({
  ChatKit: ({ className, control }: { className?: string; control: unknown }) => (
    <div className={className} data-control={String(Boolean(control))} data-testid="chatkit" />
  ),
  useChatKit: chatKitMock.useChatKit,
}));

import { App } from "./App";

describe("App", () => {
  beforeEach(() => {
    window.localStorage.clear();
    chatKitMock.useChatKit.mockReset();
    chatKitMock.useChatKit.mockReturnValue({ control: { mounted: true } });
  });

  it("renders the ChatKit component", () => {
    render(<App />);

    expect(screen.getByTestId("chatkit")).toBeTruthy();
  });

  it("uses the same-origin ChatKit endpoint by default", () => {
    render(<App />);

    expect(chatKitMock.useChatKit).toHaveBeenCalledWith(
      expect.objectContaining({
        api: expect.objectContaining({
          url: "/chatkit",
        }),
      }),
    );
  });
});
