$ = jQuery;
$(document).ready(function () {

    function run_slideshow() {
        $('.slideshow').each(function () {
                let slides = $(this).children();
                let rotate = $(this).attr('interval') * 100;
                let ndx = 0;
                let rotator = function () {
                    $.each(slides, function (a, b) {
                        $(this).hide();
                    });
                    $(slides[ndx]).show();
                    ndx++;
                    if (ndx >= slides.length) {
                        ndx = 0
                    }
                    ;
                    setTimeout(rotator, rotate);
                };
                rotator();
            }
        )
    }

    run_slideshow();
});



/* ****Need to generalize copy to clipboard to accept template specified location to copy.**** */

/* Create copy to clipboard capability to move page usage pathnames
* which have extra spaces for readability into correct pathnames.
* This assumes a structure with a table row containing the buttion in the
* first  column and the text in the second column.  */
$(".pageusagebttn").each(function (){
    var this_el = this;
    this_el.addEventListener("click", copyToClipboard)
})

function copyToClipboard(e) {
    let target = e.target;

    let copyText = target.parentElement.parentElement.children[1].textContent;
    /* Copy the text inside the text field */
    navigator.clipboard.writeText(copyText.replace(/\s+/g, ''));
    target.style.backgroundColor = 'Green';
}

/* Create copy to clipboard capability for photo filenames in sys_admin photo thumbnails.
*  This assumes the filename is in the immediately preceding element.  */
$(".photofilebttn").each(function (){
    var this_el = this;
    this_el.addEventListener("click", copyToClipboard2)
})

function copyToClipboard2(e) {
    let target = e.target;

    let copyText = target.parentElement.children[0].textContent;
    /* Copy the text inside the text field */
    navigator.clipboard.writeText(copyText.replace(/\s+/g, ''));
    target.style.backgroundColor = 'Green';
}

//# sourceURL=sst_javascript.js