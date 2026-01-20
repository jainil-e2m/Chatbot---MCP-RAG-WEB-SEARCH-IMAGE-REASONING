export type ChatModel = {
    id: string
    label: string
    provider: "openrouter" | "local"
    description?: string
}

export const CHAT_MODELS: ChatModel[] = [
    {
        id: "meta-llama/llama-3.3-70b-instruct:free",
        label: "LLaMA 3.3 70B",
        provider: "openrouter",
        description: "Best overall reasoning & chat quality",
    },
    {
        id: "mistralai/mistral-small-3.1-24b-instruct:free",
        label: "Mistral Small 24B",
        provider: "openrouter",
        description: "Strong instruction following",
    },
    {
        id: "google/gemma-3-12b-it:free",
        label: "Gemma 3 12B",
        provider: "openrouter",
    },
    {
        id: "qwen/qwen3-next-80b-a3b-instruct:free",
        label: "Qwen 3 Next 80B",
        provider: "openrouter",
        description: "Long-context reasoning",
    },
]
