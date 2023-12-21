package podevent

import "time"

type Event struct {
	ID        string
	EventType EventType
	Start     time.Time
	End       time.Time
	NodeName  string
	Deadline  time.Time
	Created   time.Time
}

type EventType int

const (
	TypeCreated EventType = iota
	TypeRunning
	TypePaused
	TypeResumed
	TypeFinished
	TypeFailed
)
