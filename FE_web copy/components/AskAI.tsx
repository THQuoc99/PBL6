import { useState, useEffect, useRef } from "react";
import { MessageCircle, Send, X, Bot, User, Check, ChevronDown, Mic, MicOff } from "lucide-react";
import { MenuItems } from "../types";
import Modal from "./ui/Modal";

// Speech Recognition type definitions
interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onresult: ((event: any) => void) | null;
  onerror: ((event: any) => void) | null;
  onend: (() => void) | null;
  start(): void;
  stop(): void;
  abort(): void;
}

declare global {
  interface Window {
    SpeechRecognition: new () => SpeechRecognition;
    webkitSpeechRecognition: new () => SpeechRecognition;
  }
}

interface Message {
  id: string;
  role: "user" | "ai";
  content: string;
  timestamp: Date;
}

interface AskAIProps {
  currentComponent: MenuItems;
  storeData?: any; // Store context data
}

export default function AskAI({ currentComponent, storeData }: AskAIProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [selectedComponent, setSelectedComponent] = useState<MenuItems>(currentComponent);
  const [isLoading, setIsLoading] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [recognition, setRecognition] = useState<SpeechRecognition | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize speech recognition
  useEffect(() => {
    if (typeof window !== "undefined") {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        const newRecognition = new SpeechRecognition();
        newRecognition.continuous = false;
        newRecognition.interimResults = false;
        newRecognition.lang = "vi-VN";
        
        newRecognition.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript;
          setInputValue(transcript);
          setIsRecording(false);
        };
        
        newRecognition.onerror = (event: any) => {
          console.error("Speech recognition error:", event.error);
          setIsRecording(false);
        };
        
        newRecognition.onend = () => {
          setIsRecording(false);
        };
        
        setRecognition(newRecognition);
      }
    }
  }, []);

  // Auto-select current component when changing pages
  useEffect(() => {
    setSelectedComponent(currentComponent);
  }, [currentComponent]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  // Component options for dropdown
  const componentOptions = [
    { value: "dashboard", label: "📊 Dashboard" },
    { value: "products", label: "📦 Products" },
    { value: "orders", label: "🛒 Orders" },
    { value: "listings", label: "📋 Listings" },
    { value: "promotions", label: "🎯 Promotions" },
    { value: "payments", label: "💳 Payments" },
    { value: "settings", label: "⚙️ Settings" },
    { value: "chatbot", label: "🤖 Chatbot" },
  ];

  // Initialize with welcome message
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([{
        id: "welcome",
        role: "ai",
        content: `👋 Hi! I'm your AI assistant for ${getComponentDisplayName(currentComponent)}. I can help you with:\n\n• Data analysis and insights\n• Best practices and recommendations\n• Troubleshooting issues\n• Store optimization tips\n\nWhat would you like to know?`,
        timestamp: new Date()
      }]);
    }
  }, []);

  const getComponentDisplayName = (component: MenuItems) => {
    const option = componentOptions.find(opt => opt.value === component);
    return option?.label || component;
  };

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    // Simulate AI response (replace with actual AI integration)
    setTimeout(() => {
      const aiResponse = generateAIResponse(inputValue, selectedComponent, storeData);
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "ai",
        content: aiResponse,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiMessage]);
      setIsLoading(false);
    }, 1000);
  };

  const startRecording = () => {
    if (recognition && !isRecording) {
      setIsRecording(true);
      recognition.start();
    }
  };

  const stopRecording = () => {
    if (recognition && isRecording) {
      recognition.stop();
    }
  };

  const handleVoiceToggle = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const generateAIResponse = (question: string, component: MenuItems, data: any) => {
    const lowerQuestion = question.toLowerCase();
    
    // Context-aware responses based on component
    const responses: Record<MenuItems, string[]> = {
      dashboard: [
        "📊 **Dashboard Insights:**\n\nI can help you analyze your store performance, revenue trends, and key metrics. What specific data would you like me to explain?",
        "Your dashboard shows real-time business metrics. I notice trends in sales, orders, and customer activity. Would you like me to dive deeper into any particular area?",
      ],
      products: [
        "📦 **Product Management:**\n\n• **Inventory optimization** - I can suggest reorder points\n• **SKU organization** - Help with categorization\n• **Pricing strategies** - Market analysis\n• **Variant management** - Size/color optimization\n\nWhat aspect interests you most?",
        "I can help optimize your product catalog, analyze inventory levels, suggest pricing strategies, or troubleshoot product-related issues.",
      ],
      orders: [
        "🛒 **Order Management:**\n\n• **Order processing** workflow optimization\n• **Shipping & fulfillment** best practices\n• **Customer communication** templates\n• **Return handling** procedures\n\nWhich area would you like guidance on?",
        "I can assist with order fulfillment, tracking issues, customer service, and optimizing your order processing workflow.",
      ],
      listings: [
        "📋 **Marketplace Listings:**\n\nI can help with listing optimization, marketplace strategies, competitive analysis, and performance tracking across different platforms.",
      ],
      promotions: [
        "🎯 **Promotion Strategy:**\n\n• **Discount optimization** - ROI analysis\n• **Campaign timing** - Seasonal strategies\n• **Customer segmentation** - Targeted offers\n• **A/B testing** - Performance comparison\n\nWhat promotion challenge can I help solve?",
      ],
      payments: [
        "💳 **Payment & Finance:**\n\nI can help with payment processing, transaction analysis, fee optimization, cash flow management, and financial reporting.",
      ],
      settings: [
        "⚙️ **Store Configuration:**\n\nI can guide you through store setup, shipping options, tax configuration, user management, and system integration.",
      ],
      chatbot: [
        "🤖 **AI Chatbot Setup:**\n\nI can help configure your customer support chatbot, create response templates, and optimize customer interactions.",
      ]
    };

    // Get relevant responses for current component
    const componentResponses = responses[component] || ["I can help you with questions about your store. What would you like to know?"];
    
    // Simple keyword matching for demo (replace with actual AI)
    if (lowerQuestion.includes('how') || lowerQuestion.includes('help')) {
      return componentResponses[0];
    } else if (lowerQuestion.includes('data') || lowerQuestion.includes('analyt')) {
      return "📈 I can analyze your store data and provide insights. What specific metrics or trends would you like me to examine?";
    } else if (lowerQuestion.includes('best') || lowerQuestion.includes('recommend')) {
      return "💡 Based on industry best practices and your store data, I can provide personalized recommendations. What area would you like me to focus on?";
    } else {
      return componentResponses[Math.floor(Math.random() * componentResponses.length)];
    }
  };

  return (
    <>
      {/* Floating AI Button */}
      <div className="fixed bottom-6 right-6 z-50">
        <button
          onClick={() => setIsOpen(true)}
          className="group relative bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-full p-4 shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200"
        >
          <MessageCircle className="h-6 w-6" />
          
          {/* Notification dot */}
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
          
          {/* Tooltip */}
          <div className="absolute bottom-full right-0 mb-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <div className="bg-gray-900 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
              Ask AI Assistant
            </div>
          </div>
        </button>
      </div>

      {/* Chat Modal */}
      <Modal
        open={isOpen}
        onClose={() => setIsOpen(false)}
        title={
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
              <Bot className="h-4 w-4 text-white" />
            </div>
            <div>
              <div className="font-semibold">AI Store Assistant</div>
              <div className="text-xs text-gray-500">Ask me anything about your store</div>
            </div>
          </div>
        }
        footer={
          <div className="flex flex-col gap-3 w-full">
            {/* Component Selector */}
            <div className="relative">
              <button
                onClick={() => setDropdownOpen(!dropdownOpen)}
                className="w-50 flex items-center justify-between px-3 py-2 bg-white border border-gray-200 rounded-xl text-sm hover:border-gray-300 transition-colors"
              >
                <div className="flex items-center gap-2">
                  <span>{componentOptions.find(opt => opt.value === selectedComponent)?.label}</span>
                </div>
                <ChevronDown className={`h-4 w-4 transition-transform ${dropdownOpen ? 'rotate-180' : ''}`} />
              </button>
              
              {dropdownOpen && (
                <div className="absolute bottom-full left-0 w-50 mb-2 bg-white border border-gray-200 rounded-xl shadow-lg max-h-60 overflow-y-auto z-10">
                  {componentOptions.map((option) => (
                    <button
                      key={option.value}
                      onClick={() => {
                        setSelectedComponent(option.value as MenuItems);
                        setDropdownOpen(false);
                      }}
                      className="w-full flex items-center gap-3 px-3 py-2.5 text-sm hover:bg-gray-50 transition-colors first:rounded-t-xl last:rounded-b-xl"
                    >
                      <div className="w-4 h-4 flex items-center justify-center">
                        {selectedComponent === option.value && (
                          <Check className="h-3 w-3 text-blue-600" />
                        )}
                      </div>
                      <span className="text-left">{option.label}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
            
            {/* Message Input */}
            <div className="flex gap-2 items-end">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                placeholder={`Ask about ${getComponentDisplayName(selectedComponent)}... (Shift+Enter for new line)`}
                rows={1}
                className="flex-1 rounded-xl border border-gray-200 px-3 py-2 text-sm outline-none focus:border-blue-500 resize-none min-h-[40px] max-h-32"
                style={{
                  height: 'auto',
                  minHeight: '40px'
                }}
                onInput={(e) => {
                  const target = e.target as HTMLTextAreaElement;
                  target.style.height = 'auto';
                  target.style.height = Math.min(target.scrollHeight, 128) + 'px';
                }}
              />
              
              {/* Voice Input Button */}
              <button
                onClick={handleVoiceToggle}
                className={`rounded-xl px-4 py-2 flex-shrink-0 h-10 transition-colors ${
                  isRecording 
                    ? 'bg-red-600 hover:bg-red-700 text-white animate-pulse' 
                    : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                }`}
                disabled={!recognition}
                title={isRecording ? "Dừng ghi âm" : "Ghi âm bằng giọng nói"}
              >
                {isRecording ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
              </button>
              
              <button
                onClick={handleSend}
                disabled={!inputValue.trim() || isLoading}
                className="bg-blue-600 text-white rounded-xl px-4 py-2 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0 h-10"
              >
                <Send className="h-4 w-4" />
              </button>
            </div>
          </div>
        }
      >
        {/* Chat Messages */}
        <div className="h-96 flex flex-col">
          <div className="flex-1 overflow-y-auto space-y-4 p-4 bg-gray-50 rounded-lg">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {message.role === 'ai' && (
                  <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
                    <Bot className="h-4 w-4 text-white" />
                  </div>
                )}
                
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-2 ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-white border border-gray-200'
                  }`}
                >
                  <div className="text-sm whitespace-pre-wrap">{message.content}</div>
                  <div className={`text-xs mt-1 ${message.role === 'user' ? 'text-blue-100' : 'text-gray-400'}`}>
                    {message.timestamp.toLocaleTimeString()}
                  </div>
                </div>
                
                {message.role === 'user' && (
                  <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center flex-shrink-0">
                    <User className="h-4 w-4 text-white" />
                  </div>
                )}
              </div>
            ))}
            
            {isLoading && (
              <div className="flex gap-3 justify-start">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
                  <Bot className="h-4 w-4 text-white" />
                </div>
                <div className="bg-white border border-gray-200 rounded-2xl px-4 py-2">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}
            
            {/* Auto scroll target */}
            <div ref={messagesEndRef} />
          </div>
        </div>
      </Modal>
    </>
  );
}