export type InterruptPayload = {
    type: "approval";
    message: string;
    options?: string[];
}

export type ServerEvent = 
    | {type: "token"; content: string}
    | {type: "interrupt"; payload: InterruptPayload}
    | {type: "error"; message: string}
    | {type: "done"}

export type ClientEvent = 
    | {type: "user_message"; content: string}
    | {type: "resume"; approved: "yes" | "no"}

export type ChatMessage = {
    role: "user" | "assistant";
    content: string;
    stream?: boolean;
}