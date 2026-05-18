import { ChatKit, useChatKit } from "@openai/chatkit-react";

const apiBaseUrl =
  (import.meta.env.VITE_API_BASE_URL as string | undefined)?.trim().replace(/\/$/, "") || "";
const chatkitApiUrl = apiBaseUrl ? `${apiBaseUrl}/chatkit` : "/chatkit";
const domainKey =
  (import.meta.env.VITE_CHATKIT_DOMAIN_KEY as string | undefined)?.trim() || "local-dev";

export function App() {
  const { control } = useChatKit({
    api: {
      url: chatkitApiUrl,
      domainKey,
      fetch: (input, init) => {
        const existingHeaders = new Headers(init?.headers);
        const storedUserId = getStarterUserId();
        existingHeaders.set("x-starter-user-id", storedUserId);
        return fetch(input, {
          ...init,
          headers: existingHeaders,
        });
      },
    },
    theme: {
      colorScheme: "light",
      radius: "round",
      density: "normal",
      typography: {
        baseSize: 15,
        fontFamily: "\"IBM Plex Sans\", \"Avenir Next\", \"Segoe UI\", sans-serif",
      },
    },
    composer: {
      placeholder: "Ask the starter how the scaffold is wired…",
    },
    history: {
      enabled: true,
      showDelete: true,
      showRename: true,
    },
    threadItemActions: {
      feedback: true,
      retry: true,
    },
    startScreen: {
      greeting: "Chat with the starter scaffold",
      prompts: [
        {
          label: "Inspect runtime",
          prompt: "Summarize the current runtime scaffold and the main extension seams.",
          icon: "sparkle",
        },
        {
          label: "Ask about agents",
          prompt: "Explain how the starter agent registry is structured.",
          icon: "compass",
        },
      ],
    },
    initialThread: window.localStorage.getItem("starter-chat-thread-id") || undefined,
    onThreadChange: ({ threadId }) => {
      if (threadId) {
        window.localStorage.setItem("starter-chat-thread-id", threadId);
      }
    },
  });

  return (
    <main className="app-shell">
      <section className="hero-panel">
        <p className="eyebrow">Optional Accelerator</p>
        <h1>ChatKit Starter</h1>
        <p className="lede">
          This frontend is an optional scaffold over the generic backend chat service. Keep it,
          swap it, or delete it in downstream repos.
        </p>
        <dl className="fact-grid">
          <div>
            <dt>Backend</dt>
            <dd>Self-hosted ChatKit adapter</dd>
          </div>
          <div>
            <dt>Traces</dt>
            <dd>Native ChatKit tool and agent activity</dd>
          </div>
          <div>
            <dt>Identity</dt>
            <dd>Anonymous local user seam</dd>
          </div>
        </dl>
      </section>
      <section className="chat-panel">
        <div className="chat-frame">
          <ChatKit control={control} className="chatkit-root" />
        </div>
      </section>
    </main>
  );
}

function getStarterUserId(): string {
  const storageKey = "starter-chat-user-id";
  const existing = window.localStorage.getItem(storageKey);
  if (existing) {
    return existing;
  }
  const generated = `starter-user-${crypto.randomUUID()}`;
  window.localStorage.setItem(storageKey, generated);
  return generated;
}
