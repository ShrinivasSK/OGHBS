// const signUpButton = document.getElementById('signUp');
var signInButton=document.getElementById('login');
// console.log(signInButton);
// // const container = document.getElementById('container');

var emailTextBox=document.getElementById('email');
var passwordTextBox=document.getElementById('password'); 

// signUpButton.addEventListener('click', () => {
// 	container.classList.add("right-panel-active");
// });

signInButton.addEventListener('click', () => {
    // container.classList.remove("right-panel-active");
    var email=emailTextBox.value;
    var password=passwordTextBox.value;
    console.log(email);
    console.log(password);
});