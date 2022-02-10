
if (document.querySelectorAll("#chesser").length > 0)
{
    function htmlToElement(html) {
        var template = document.createElement('template');
        html = html.trim(); // Never return a text node of whitespace as the result
        template.innerHTML = html;
        return template.content.firstChild;
    };

    document.getElementById("chesser").addEventListener("keyup", function(event) {
        if (event.key === "Enter") {
            event.preventDefault();
            if (document.getElementById("chesser").value.length > 0) {
                var xhttp = new XMLHttpRequest();
                xhttp.onreadystatechange = function() {
                    if (this.readyState == 4 && this.status == 200) {
                        location.reload();
                    };
                };
                var theUrl = "/api/chess/play";
                xhttp.open("POST", theUrl);
                var data = new FormData();
                data.append("query", document.getElementById("chesser").value );
                xhttp.send(data);
                document.getElementById("chesser").value = "";
            }
        }
    });
    document.getElementById("chesser").focus()

    function reload(){
        //location.reload()
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                var obj = document.querySelectorAll(".board")[0]
                obj.removeChild(obj.firstChild);
                document.querySelectorAll(".board")[0].appendChild(htmlToElement(this.responseText));
                setTimeout(reload, 2000);
            };
        };
        var theUrl = "/api/chess/svg";
        xhttp.open("GET", theUrl);
        xhttp.send();
    }

    if (window.location.search == "?refresh") {
        document.querySelectorAll(".chesser")[0].style.display = 'none';
        setTimeout(reload, 2000);
    }
}