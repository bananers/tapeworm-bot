package main

import tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api"

// Actions defines what to do with a response object
type Actions int

const (
	// ActionNOOP indicates to do nothing
	ActionNOOP Actions = iota

	// ActionReply indicates to send a response back
	ActionReply
)

func (a Actions) String() string {
	if a == ActionNOOP {
		return "NOOP"
	} else if a == ActionReply {
		return "Reply"
	} else {
		return "Unknown"
	}
}

// MessageHandler takes in telegram API messages and outputs an action and the corresponding message
type MessageHandler struct{}

func (m *MessageHandler) process(message tgbotapi.Message) (Actions, tgbotapi.MessageConfig) {
	text := message.Text
	if text == "ping" {
		reply := tgbotapi.NewMessage(message.Chat.ID, "pong")
		reply.ReplyToMessageID = message.MessageID
		return ActionReply, reply
	}

	return ActionNOOP, tgbotapi.MessageConfig{}
}
