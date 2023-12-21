var otp_inputs = document.querySelectorAll(".otp__digit")
var mykey = "0123456789".split("")
otp_inputs.forEach((_) => {
    _.addEventListener("keyup", handle_next_input)
})

function handle_next_input(event) {
    let current = event.target
    let index = parseInt(current.classList[1].split("__")[2])
    current.value = event.key

    if (event.keyCode == 8 && index > 1) {
        current.previousElementSibling.focus()
    }
    if (index < 6 && mykey.indexOf("" + event.key + "") != -1) {
        var next = current.nextElementSibling;
        next.focus()
    }
    var _finalKey = ""
    for (let { value } of otp_inputs) {
        _finalKey += value
    }
    var otpElement = document.querySelector("#_otp");
    otpElement.classList.replace(_finalKey.length === 6 ? "_notok" : "_ok", _finalKey.length === 6 ? "_ok" : "_notok");
    otpElement.innerText = _finalKey;
}
