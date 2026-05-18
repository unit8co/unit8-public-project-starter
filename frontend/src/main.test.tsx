import { waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("./App", () => ({
  App: () => <div data-testid="starter-app" />,
}));

describe("main", () => {
  it("renders the starter app into the root element", async () => {
    document.body.innerHTML = '<div id="root"></div>';

    await import("./main");

    await waitFor(() => {
      expect(document.querySelector('[data-testid="starter-app"]')).toBeTruthy();
    });
  });
});
