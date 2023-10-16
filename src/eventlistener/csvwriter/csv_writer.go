package csvwriter

type Writer interface {
	Open(filename string) error
	Append(line []string)
	Close()
}
