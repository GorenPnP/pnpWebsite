// chosen fields, key is type (IP, AP, ...)
var selected_fields = {};


function submitPrio() {
    post(selected_fields);
}


document.addEventListener("DOMContentLoaded", function () {


    var apDept = document.querySelector("#ap-debt");
    var apLeft = document.querySelector("#ap-left");
    var apDebtText = document.querySelector("#ap-debt-text");
    var apLeftText = document.querySelector("#ap-left-text")
    var submit_btn  = document.querySelector("#submit");

    var selected = 'selected';
    var blocked = 'blocked';

    var row_len = 6;
    var rows = 6;

    for (var i = 0; i < rows; i++) selected_fields[i] = -1;

    // 2d array[rows][row_len] for blocked elements
    var blocked_fields = Array.from({length:rows}, () => Array.from({length:row_len}, () => 0))

    function getId(i, j) {
        return i.toString() + "|" + j.toString();
    }


    /* start of logic */
    for (var i_outer = 0; i_outer < rows; i_outer++) {

        for (var j_outer = 0; j_outer < row_len; j_outer++) {
            var td_tag = document.getElementById(getId(i_outer, j_outer));

            td_tag.addEventListener('click', function (event) {

                type = parseInt(/^\d+/.exec(this.id));
                prio = parseInt(/\d+$/.exec(this.id));
                var select;


                // element is blocked or bas no (numeral) content => do nothing
                if (blocked_fields[type][prio] || !(/\d+/.test( this.innerHTML )) ) return;

                // unmark now
                if (this.classList.contains(selected)) {
                    select = false;
                    this.classList.remove(selected);
                    selected_fields[type] = -1

                    //  calc ap_cost (more debt)
                    if (type === 1) {
                        var ap_cost = parseInt(apDept.innerHTML);
                        ap_cost += parseInt(/\d+/.exec(this.innerHTML));

                        apDept.innerHTML = ap_cost;
                    }
                }

                // mark now
                else {
                    select = true;
                    this.classList.add(selected);
                    selected_fields[type] = prio;

                    //  calc ap_cost (less debt)
                    if (type === 1) {
                        var ap_cost = parseInt(apDept.innerHTML);
                        ap_cost -= parseInt(/\d+/.exec(this.innerHTML));

                        apDept.innerHTML = ap_cost;
                    }
                }

                // handle blocked
                for (var row = 0; row < rows; row++) {
                    for (var col = 0; col < row_len; col++) {

                        // ignore own element
                        if (row === type && col === prio) continue;

                        tag = document.getElementById(getId(row, col));

                        // found one to (un-)block
                        if ((!tag.classList.contains(selected)) &&
                            (row === type || col === prio)) {

                            if (select) {
                                if (0 === blocked_fields[row][col]++) {
                                    // mark as blocked
                                    tag.classList.add(blocked);
                                }
                            }
                            else {
                                if (!(--blocked_fields[row][col])) {
                                    // unmark blocked
                                    tag.classList.remove(blocked);
                                }
                            }
                        }
                    }
                }

                // handle ap-debt/ap-left
                if (parseInt(apDept.innerHTML) <= 0) {      // no debt
                    apDebtText.style.display = "none";
                    apLeftText.style.display = "inline-block";
                    apLeft.innerHTML = parseInt(apDept.innerHTML) * -1;
                } else {
                    apDebtText.style.display = "inline-block";
                    apLeftText.style.display = "none";
                }

                // set to submittable form value & handle btn
                //formData.value = JSON.stringify(selected_fields)
                submit_btn.disabled = Object.values(selected_fields).includes(-1) || parseInt(apDept.innerHTML) > 0;
            });
        }
    }
}); // document ready
