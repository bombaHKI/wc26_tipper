function openClose(el) {
    parent = el.parentElement;
    content = el.nextElementSibling;

    parent.classList.toggle("open");
    if (parent.classList.contains("open"))
        content.style.maxHeight = content.scrollHeight + "px";
    else
        content.style.maxHeight = "0";
}