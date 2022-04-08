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

var button_state = (function () {
    let al_state = false;
    let il_state = true;
    let religion_state = false;
    let wellness_state = false;
    let event_state = true;
    let club_state = false;
    let community_state = false;
    let audiences = [al_state, il_state];
    let audience_names = ['AL', 'IL'];
    let audience_classes = ['fc-al_button-button', 'fc-il_button-button'];
    let categories = [event_state, wellness_state, religion_state, club_state, community_state];
    let category_names = ['Event', 'Wellness', 'Religion', 'Resident Clubs', 'Community'];
    let category_classes = ['fc-evt_button-button', 'fc-well_button-button', 'fc-rel_button-button',
        'fc-club_button-button', 'fc-community_button-button'];
    return {
        initialize: function () {
            //Do anything needed here
        },
        set_audience: function (btn) {
            for (let i = 0; i < audiences.length; i++) {
                audiences[i] = false;
                $('.' + audience_classes[i]).removeClass('sst-highlight');
                if (btn.textContent == audience_names[i]) {
                    audiences[i] = true;
                    $('.' + audience_classes[i]).addClass('sst-highlight');
                }
            }
        },
        color_buttons: function (info) {
            for (let i = 0; i < audiences.length; i++) {
                $('.' + audience_classes[i]).removeClass('sst-highlight');
                if (audiences[i]) {
                    $('.' + audience_classes[i]).addClass('sst-highlight');
                }
            }
            ;
            for (let i = 0; i < categories.length; i++) {
                $('.' + category_classes[i]).removeClass('sst-highlight');
                if (categories[i]) {
                    $('.' + category_classes[i]).addClass('sst-highlight');
                }
            }
            ;
        },
        set_category: function (btn) {
            let res = '';
            for (let i = 0; i < categories.length; i++) {
                categories[i] = false;
                if (btn.textContent == category_names[i]) {
                    categories[i] = true;
                    res = category_names[i];
                }
            }
        },
        get_audience: function () {
            for (let i = 0; i < audiences.length; i++) {
                if (audiences[i]) {
                    return audience_names[i];
                }
            }
        },
        get_category: function () {
            for (let i = 0; i < categories.length; i++) {
                if (categories[i]) {
                    return category_names[i];
                }

            }
        },
    }
})();

/* Rotation based on Next/Prev button */
var $divs = $(".newRes"),
    index = 0;
$("#prevRes").hide()

$("#nextRes").click(function () {
    updateStatus(1);
});

$("#prevRes").click(function () {
    updateStatus(-1);
});
$(".newRes").hide()

function updateStatus(a) {

    $divs.eq(index).removeClass("current").hide();
    index += a;
    $divs.eq(index).addClass("current").show();
    $("#nextRes").toggle(index !== $divs.length - 1);
    $("#prevRes").toggle(index !== 0);
    var pos = index + 1;
    $("#locRes").each(function () {
        var txt = $(this).text().replace(/.*/, "Resident " + pos + " of " + $divs.length);
        $(this).text(txt);
    })
}

updateStatus(0);

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