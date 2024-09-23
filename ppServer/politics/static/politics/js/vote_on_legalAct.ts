/**************************** LEGAL ACT ***********************************/

// init LegalAct form stuff
new EasyMDE({
     ...MDEditorConfig,
     element: document.querySelector("#id_text") as any as HTMLElement,
});


/****************************** VOTES *************************************/
interface Vote {
     vote: "y" | "n" | "a" | "e";
     legal_act: number;
     politician: Politician;
};

interface Politician {
     id: number;
     name: string;
     is_party_lead: boolean;
     genere: string;
     party: number;
     portrait: string;
     birthyear: number;
};


// get data as typed ts-objects
const all_parties = JSON.parse(document.querySelector("#parties")!.innerHTML) as Party[];
const votes = JSON.parse(document.querySelector("#votes")!.innerHTML) as Vote[];

all_parties.forEach(party => {
     // set num politicians
     document.querySelector(`#header-party-${party.id} .members`)!.innerHTML = ""+votes.filter(vote => vote.politician.party === party.id).length;
     // set politicians with their votes
     construct_politicians(party);
     // update checkboxes of party with information about politicians' votes
     update_party(party.id);

     // listen for changes of party's checkboxes. Change party's politicians votes accordingly
     document.querySelectorAll(`#header-party-${party.id} .form-check-input`).forEach(checkbox_tag => checkbox_tag.addEventListener("input", function() {
          update_votes(this, party.id);
          update_result();
     }))
     // listen for changes of party's politicians' votes. Change party's checkboxes accordingly
     document.querySelectorAll(`#party-${party.id} .form-check-input`).forEach(radio_tag =>radio_tag.addEventListener("input", function() {update_party(party.id); update_result()}))
});

// don't toggle accordion on interaction with its header's buttons
document.querySelectorAll(".party__select-utils").forEach(utils_container => {
     const attr = 'data-bs-toggle';
     const accordionButton = utils_container.closest(`[${attr}]`);
     utils_container.addEventListener('mouseenter', () => accordionButton!.setAttribute(attr, ''));
     utils_container.addEventListener('mouseleave', () => accordionButton!.setAttribute(attr, 'collapse'));
});

// update final voting results (displayed in a table)
update_result();

/** adds html of all party's politicians into accordion body */
function construct_politicians(party: Party): void {
     const votes_of_party = votes
          .filter(vote => vote.politician.party === party.id)
          .map(vote => `<li class="list-group-item">
               <div class="party__politician">
                    <span>${vote.politician.name || "<i>Name</i>"} (${vote.politician.genere || "<i>Genere</i>"}) - ${vote.politician.birthyear || "<i>Geburtsjahr</i>"}</span>
                    <div class="party__select-utils">
                         <div class="form-check">
                              <input class="form-check-input" type="radio" ${vote.vote === 'y' ? 'checked' : ''} name="politician-${vote.politician.id}" id="vote-${vote.politician.id}-y" value="y">
                              <label class="form-check-label" for="vote-${vote.politician.id}-y">Ja</label>
                         </div>
                         <div class="form-check">
                              <input class="form-check-input" type="radio" ${vote.vote === 'n' ? 'checked' : ''} name="politician-${vote.politician.id}" id="vote-${vote.politician.id}-n" value="n">
                              <label class="form-check-label" for="vote-${vote.politician.id}-n">Nein</label>
                         </div>
                         <div class="form-check">
                              <input class="form-check-input" type="radio" ${vote.vote === 'e' ? 'checked' : ''} name="politician-${vote.politician.id}" id="vote-${vote.politician.id}-e" value="e">
                              <label class="form-check-label" for="vote-${vote.politician.id}-e">Enthalten</label>
                         </div>
                         <div class="form-check">
                              <input class="form-check-input" type="radio" ${vote.vote === 'a' ? 'checked' : ''} name="politician-${vote.politician.id}" id="vote-${vote.politician.id}-a" value="a">
                              <label class="form-check-label" for="vote-${vote.politician.id}-a">Abwesend</label>
                         </div>
                    </div>
               </div></li>`
          );

     document.querySelector(`#party-${party.id} .accordion-body`)!.innerHTML =
          '<ul class="list-group list-group-flush">' + votes_of_party.join("") + "</ul>";
}

/** set party's checkboxes according to party's politicians' votes. can be unchecked, indeterminate or checked */
function update_party(party_id: number): void {
     const party = all_parties.find(party => party.id === party_id)!;
     const politicians = [...document.querySelectorAll(`#party-${party.id} .form-check-input:checked`)] as any[];

     const header = document.querySelector(`#header-party-${party.id}`)!;
     // clear every header checkbox
     header.querySelectorAll(".form-check-input").forEach((checkbox: any) => {
          checkbox.checked = false;
          checkbox.indeterminate = false;
          checkbox.style.backgroundImage = "unset";
     });

     if (politicians.length) {
          // set header checkboxes
          politicians
               .reduce((acc, pol) => {
                    acc.add(pol.value);
                    return acc;
               }, new Set())
               .forEach((choice: string, _: number, choices: Set<string>) => {
                    const mark_color = getComputedStyle(header).getPropertyValue('--bs-accordion-btn-bg').slice(1);
                    const input_tag = header.closest(".accordion-item")!.querySelector(`#party-${party.abbreviation}-${choice}`) as any;
                    if (choices.size === 1) {
                         input_tag.style.backgroundImage = `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20'%3e%3cpath fill='none' stroke='%23${mark_color}' stroke-linecap='round' stroke-linejoin='round' stroke-width='3' d='m6 10 3 3 6-6'/%3e%3c/svg%3e")`;
                         return input_tag.checked = true;
                    }
                    input_tag.indeterminate = true;
                    input_tag.style.backgroundImage = `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20'%3e%3cpath fill='none' stroke='%23${mark_color}' stroke-linecap='round' stroke-linejoin='round' stroke-width='3' d='M6 10h8'/%3e%3c/svg%3e")`;
               });

     } else {
          // disable header & its checkboxes
          (header as any).disabled = true;
          header.querySelectorAll(".party__select-utils .form-check-input").forEach((input: any) => input.disabled = true);
     }
}

/** receives a party's checkbox and sets all party's politicians' votes to that checkbox if it is checked */
function update_votes(checkbox_tag: any, party_id: number) {
     const vote = checkbox_tag.id.split("-").reverse()[0];
     if (!checkbox_tag.checked) { return; }

     document.querySelectorAll(`#party-${party_id} .form-check-input[value=${vote}]`).forEach((radio_tag: any) => radio_tag.checked = true);
     update_party(party_id);
     update_result();
}

/** updates the voting result table */
function update_result() {
     const votes_by_category = [...document.querySelectorAll("#party-votes .party__politician .form-check-input:checked")]
          .reduce((acc, radio: any) => {
               acc[radio.value as string] = acc[radio.value as string] ? acc[radio.value as string]+1 : 1;
               return acc;
          }, {} as {[category: string]: number});
     const total_votes = Object.values(votes_by_category).reduce((acc, num) => acc + num, 0);

     document.querySelectorAll(".vote-result").forEach(tag => {
          tag.innerHTML = `${(votes_by_category[tag.id.split('-').reverse()[0]] || 0) *100 / total_votes}%`;
     });
}