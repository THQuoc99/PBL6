import { useState } from "react";
import { ToolbarButton } from "../../index";

type Message = { id: string; from: "buyer" | "ai" | "seller"; text: string; time: string };

type Conversation = { id: string; buyerName: string; messages: Message[]; aiEnabled: boolean };

const sample: Conversation[] = [
  {
    id: "C1",
    buyerName: "Alice",
    aiEnabled: true,
    messages: [
      { id: "m1", from: "buyer", text: "Is this available in blue?", time: new Date().toISOString() },
      { id: "m2", from: "ai", text: "Yes, we have it in blue and black.", time: new Date().toISOString() },
    ],
  },
  {
    id: "C2",
    buyerName: "Bob",
    aiEnabled: false,
    messages: [
      { id: "m3", from: "buyer", text: "What's the delivery time to Hanoi?", time: new Date().toISOString() },
    ],
  },
];

export default function ChatbotAIPage() {
  const [conversations, setConversations] = useState<Conversation[]>(sample);
  const [activeId, setActiveId] = useState<string | null>(conversations[0]?.id ?? null);
  const [input, setInput] = useState("");

  const activeConv = conversations.find(c => c.id === activeId) ?? null;

  const sendMessage = () => {
    if (!activeConv || !input.trim()) return;
    const msg = { id: `m${Date.now()}`, from: "seller" as const, text: input.trim(), time: new Date().toISOString() };
    setConversations(conversations.map(c => c.id === activeConv.id ? { ...c, messages: [...c.messages, msg] } : c));
    setInput("");
  };

  const toggleAI = (id: string) => {
    setConversations(conversations.map(c => c.id === id ? { ...c, aiEnabled: !c.aiEnabled } : c));
  };

  const intervene = (id: string) => {
    // turn off AI and add a system message noting seller intervened
    setConversations(conversations.map(c => c.id === id ? { ...c, aiEnabled: false, messages: [...c.messages, { id: `m${Date.now()}`, from: "seller", text: "Seller has taken over the chat.", time: new Date().toISOString() }] } : c));
    setActiveId(id);
  };

  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-[300px_1fr]">
      <aside className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-lg font-semibold">Chatbot AI</h3>
          <span className="text-sm text-gray-500">Conversations</span>
        </div>
        <div className="space-y-2">
          {conversations.map(c => (
            <div key={c.id} className={`rounded-lg p-3 ${activeId === c.id ? 'bg-gray-100' : 'hover:bg-gray-50'}`} onClick={() => setActiveId(c.id)}>
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">{c.buyerName}</div>
                  <div className="text-xs text-gray-500">{c.messages[c.messages.length - 1]?.text}</div>
                </div>
                <div className="text-xs text-gray-500">{c.aiEnabled ? 'AI' : 'Human'}</div>
              </div>
              <div className="mt-2 flex gap-2">
                <button className="text-xs rounded-md border px-2 py-1" onClick={() => toggleAI(c.id)}>{c.aiEnabled ? 'Disable AI' : 'Enable AI'}</button>
                <button className="text-xs rounded-md border px-2 py-1" onClick={() => intervene(c.id)}>Intervene</button>
              </div>
            </div>
          ))}
        </div>
      </aside>

      <main>
        <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
          {!activeConv ? (
            <div className="text-center text-gray-500">Select a conversation</div>
          ) : (
            <div className="flex flex-col gap-4">
              <div className="mb-2 flex items-center justify-between">
                <h3 className="text-lg font-semibold">{activeConv.buyerName}</h3>
                <div className="text-sm text-gray-500">{activeConv.aiEnabled ? 'AI responding' : 'Seller responding'}</div>
              </div>

              <div className="max-h-[50vh] overflow-y-auto space-y-2 border-t pt-3">
                {activeConv.messages.map(m => (
                  <div key={m.id} className={`p-3 rounded-lg ${m.from === 'buyer' ? 'bg-gray-100 self-start' : m.from === 'ai' ? 'bg-indigo-50 self-end' : 'bg-green-50 self-end'}`}>
                    <div className="text-sm text-gray-800">{m.text}</div>
                    <div className="mt-1 text-xs text-gray-400">{new Date(m.time).toLocaleString()}</div>
                  </div>
                ))}
              </div>

              <div className="mt-3 flex items-center gap-2">
                <input
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    // Send message on Enter (no Shift)
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      sendMessage();
                    }
                  }}
                  placeholder="Write a message..."
                  className="flex-1 rounded-xl border p-2"
                />
                <ToolbarButton onClick={sendMessage}>Send</ToolbarButton>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
