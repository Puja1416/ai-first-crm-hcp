import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { api } from "./api";

export const fetchHcps = createAsyncThunk("interactions/fetchHcps", async () => {
  const response = await api.get("/hcps");
  return response.data;
});

export const fetchInteractions = createAsyncThunk(
  "interactions/fetchInteractions",
  async () => {
    const response = await api.get("/interactions");
    return response.data;
  }
);

export const saveInteraction = createAsyncThunk(
  "interactions/saveInteraction",
  async (payload) => {
    const response = await api.post("/interactions", payload);
    return response.data;
  }
);

export const sendAgentMessage = createAsyncThunk(
  "interactions/sendAgentMessage",
  async (message) => {
    const response = await api.post("/agent/chat", { message });
    return response.data;
  }
);

const interactionSlice = createSlice({
  name: "interactions",
  initialState: {
    hcps: [],
    items: [],
    messages: [
      {
        role: "assistant",
        text:
          "Tell me what you need: search an HCP, summarize notes, recommend follow-up, log an interaction, or edit one.",
      },
    ],
    loading: false,
    error: null,
  },
  reducers: {
    addUserMessage(state, action) {
      state.messages.push({ role: "user", text: action.payload });
    },
    clearError(state) {
      state.error = null;
    },
  },
  extraReducers(builder) {
    builder
      .addCase(fetchHcps.fulfilled, (state, action) => {
        state.hcps = action.payload;
      })
      .addCase(fetchInteractions.fulfilled, (state, action) => {
        state.items = action.payload;
      })
      .addCase(saveInteraction.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(saveInteraction.fulfilled, (state, action) => {
        state.loading = false;
        state.items.unshift(action.payload);
      })
      .addCase(saveInteraction.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      .addCase(sendAgentMessage.pending, (state) => {
        state.loading = true;
      })
      .addCase(sendAgentMessage.fulfilled, (state, action) => {
        state.loading = false;
        state.messages.push({
          role: "assistant",
          text: action.payload.message,
          data: action.payload.data,
        });
      })
      .addCase(sendAgentMessage.rejected, (state, action) => {
        state.loading = false;
        state.messages.push({
          role: "assistant",
          text:
            action.error.message ||
            "The AI assistant could not complete the request.",
        });
      });
  },
});

export const { addUserMessage, clearError } = interactionSlice.actions;
export default interactionSlice.reducer;
