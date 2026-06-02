function headerClassDecider() {
    const header = document.getElementsByTagName("header")[0];
    const mainNav = document.getElementById("main-nav");
    const logo = document.getElementById("logo");
    const userMenu = document.getElementById("user-menu");
    
    header.classList.remove("small-header");
    if ( Math.max( (userMenu.getBoundingClientRect().left - logo.getBoundingClientRect().right),
                    (logo.getBoundingClientRect().left - mainNav.getBoundingClientRect().right)) < 30)
        header.classList.add("small-header");
}
document.addEventListener('DOMContentLoaded', () => {
    headerClassDecider();
    window.addEventListener("resize", headerClassDecider);

    Array.from(document.getElementsByClassName("menu-gomb")).forEach( el => {
        el.addEventListener("click", event => {
            event.target.closest(".menu").classList.toggle("active");
        });
    });
    Array.from(document.getElementsByClassName("dropdown")).forEach( el => {
        el.addEventListener("mouseleave", event => {
            event.target.parentElement.classList.remove("active");
        });
    });
    Array.from(document.getElementsByClassName("dropdown-blur-layer")).forEach( el => {
        el.addEventListener("click", event => {
            event.target.parentElement.classList.remove("active");
        });
    });
    Array.from(document.querySelectorAll(
        'input:not(.menu .header-gomb), \
        select:not(.menu .header-gomb), \
        textarea:not(.menu .header-gomb), \
        button:not(.menu .header-gomb), \
        a:not(.menu .header-gomb), \
        [tabindex]:not(.menu .header-gomb), \
        [contenteditable]:not(.menu .header-gomb)'
      )).forEach( el => el.addEventListener("focus", () => {
        Array.from(document.getElementsByClassName("menu")).forEach(menu => {
            menu.classList.remove("active");
        });
      }));
});