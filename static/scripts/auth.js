function signUpCheckPassword(){
    let pw = document.getElementById("pw").value
    let repw = document.getElementById("re-pw").value
    let username = document.getElementById("username").value
    let signUpSibmit = document.getElementById("sign-up-btn")
    if(username.length < 3){
        document.getElementById("re-pw-alert").innerText = "Username Must Be At Least 3 Charachters"
    }
    if(pw.length < 7){
        document.getElementById("re-pw-alert").innerText = "Password Must Be At Least 8 Charachters"
    }
    if(pw != repw){
        document.getElementById("re-pw-alert").innerText = "Passwords Does Not Match"
    }
    if(pw == repw && pw.length > 7 && username.length > 3){
        document.getElementById("re-pw-alert").innerText = ""
        signUpSibmit.disabled = false
    }
}

let login = false;
function switcher(){
    login = !login
    let switcher = document.getElementById("switcher")
    let loginn = document.getElementById("login")
    let signup = document.getElementById("signUp")

    if(!login){
        switcher.innerText = "Sign Up?"
        loginn.style = "display:unset"
        signup.style = "display:none"
        
    }
    else{
        switcher.innerText = "Login?"
        loginn.style = "display:none"
        signup.style = "display:unset"
    }
}
window.onload = () => {
    switcher()
}