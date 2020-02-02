package main

import (
	"math/rand"
	"testing"

	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api"
	"github.com/stretchr/testify/require"
)

func fakeChatID() int64 {
	return rand.Int63()
}

func fakeMessageID() int {
	return rand.Int()
}

func requireActionEquals(t *testing.T, want Actions, got Actions) {
	t.Helper()
	require.Equal(t, want.String(), got.String())
}

func TestBotDoesNotReplyOnUnknownMessages(t *testing.T) {
	messageHandler := &MessageHandler{}

	message := tgbotapi.Message{
		Text: "qqq",
		Chat: &tgbotapi.Chat{
			ID: fakeChatID(),
		},
	}
	action, _ := messageHandler.process(message)

	requireActionEquals(t, ActionNOOP, action)
}

func TestBotRepliesToPing(t *testing.T) {
	messageHandler := &MessageHandler{}

	message := tgbotapi.Message{
		Text:      "ping",
		MessageID: fakeMessageID(),
		Chat: &tgbotapi.Chat{
			ID: fakeChatID(),
		},
	}
	action, reply := messageHandler.process(message)

	requireActionEquals(t, ActionReply, action)
	require.Equal(t, "pong", reply.Text)
	require.Equal(t, message.MessageID, reply.ReplyToMessageID)
}
