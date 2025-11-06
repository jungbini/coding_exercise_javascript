class People {
    constructor(name) {		// 생성자
        this.name = name;
    }
    printName() {
        console.log(this.name);
    }
}
const foo = new People('foo-name');
foo.printName();			// foo-name
