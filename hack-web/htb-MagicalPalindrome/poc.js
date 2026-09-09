import { type } from "node:os";

const test_string = "1000";
for (const index of Array(test_string.length).keys()) {
    console.log(`IndexL ${index}, Character: ${test_string[index]}`);
}

console.log("\n")
const test_json = {'length': "1000"}
console.log(test_json.length)
console.log(Array(test_json.length))

for (const index of Array(test_json.length).keys()) {
    console.log(`IndexL ${index}, Character: ${test_string[index]}`);
    console.log(test_json[index]);
}

console.log("\n")
const test_json2 = {'length': "1000", "0": "hacked"}
console.log(test_json2.length)
console.log(Array(test_json2.length))

for (const index of Array(test_json2.length).keys()) {
    console.log(`IndexL ${index}, Character: ${test_string[index]}`);
    console.log(test_json2[index]);
}


console.log("\n")
const IsPalinDrome = (string) => {
    if (string.length < 1000) {
        return 'Tootus Shortus';
    }
    
    for (const i of Array(string.length).keys()) {

        const original = string[i];
        const reverse = string[string.length - i - 1];
        
        if (original !== reverse || typeof original !== 'string') {
            return 'Notter Palindromer!!';
        }
    }

    console.log("Berhasil bypass palindrom!!!")
    return null;
}

const payload = {'length': "1000", '0': "H", "999": "H"}
const error = IsPalinDrome(payload);
console.log(error);