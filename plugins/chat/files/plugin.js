var adddialog = `
<div class="dialog">
    <div>
        <div class="siimple-tip siimple-tip--primary">
        </div>
    </div>
</div>
`;
var addresponse = `
<div class="response">
    <div>
        <div class="siimple-tip siimple-tip--success">
        coucou
        </div>
    </div>
</div>
`;

var lastepoch = 0;

function htmlToElement(html) {
    var template = document.createElement('template');
    html = html.trim(); // Never return a text node of whitespace as the result
    template.innerHTML = html;
    return template.content.firstChild;
};

document.getElementById("chatter").addEventListener("keyup", function(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        if (document.getElementById("chatter").value.length > 0) {
            document.getElementById("chat").appendChild(htmlToElement(adddialog));
            document.querySelector(".dialog:last-child .siimple-tip").textContent = document.getElementById("chatter").value;
            var xhttp = new XMLHttpRequest();
            var theUrl = "/api/query";
            xhttp.open("POST", theUrl);
            var data = new FormData();
            data.append("query", document.getElementById("chatter").value );
            xhttp.send(data);
            document.getElementById("chatter").value = "";
            document.getElementById("chatter").focus()
        }
    }
});

function updateSay(){  
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            responses = JSON.parse(this.responseText)['responses']
            if (lastepoch == 0){
                responses.forEach(function(obj){
                    if (obj['epoch'] > lastepoch){
                        lastepoch = obj['epoch'];
                    };
                });
                if (lastepoch == 0){ lastepoch = 1;}
            }else{
                responses.forEach(function(obj){
                    if (obj['epoch'] > lastepoch){
                        document.getElementById("chat").appendChild(htmlToElement(addresponse));
                        document.querySelector(".response:last-child .siimple-tip").textContent = obj['response'];
                        lastepoch = obj['epoch'];
                    };                     
                });
            }
            setTimeout(updateSay, 1000)
        };
    };
    xhttp.open("GET", "/api/responses", true);
    xhttp.send();
}

document.getElementById("chatter").focus();
updateSay();
