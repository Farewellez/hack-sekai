// https://github.com/kubernetes/kubernetes/issues/64612
// https://stackoverflow.com/questions/49006073/json-unmarshal-struct-case-sensitively
// https://www.w3schools.com/go/go_struct.php
// https://share.google/aimode/39IZWiHAnZWZcKa5W

package main

import (
	"encoding/json"
	"fmt"
)

type RequestData struct {
	Action string
}

func main() {
	payload1 := []byte(`{
		"action": "getSecureCode"
	}`)
	
	var requestData1 RequestData
	if err := json.Unmarshal(payload1, &requestData1); err != nil {
		fmt.Println("Error: ", err)
		return
	}
	fmt.Printf("Nilai ahir yang diambil Go (Versi PoC case-insensitive): %s\n", requestData1.Action)
	
	payload2 := []byte(`{
		"action": "getSecureCode",
		"Action": "getcosmic"
	}`)

	var requestData2 RequestData
	if err := json.Unmarshal(payload2, &requestData2); err != nil {
		fmt.Println("Error: ", err)
		return
	}

	fmt.Printf("Nilai ahir yang diambil Go (Versi Timpa field Action): %s\n", requestData2.Action)
}