function returnArray() {
    return [1, 2, 3];
}

const [one, , three] = returnArray();
console.log(one);		// 1
console.log(three);		// 3
