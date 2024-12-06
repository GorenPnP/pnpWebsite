// config
const politician_diameter = 20;
const overall_angle = 178;
const initial_radius = 4*politician_diameter;

interface Politician {
    portrait: string,
    name: string,
    is_party_lead: boolean,
    genere: string,
    birthyear: number,

    vote?: string,
};
interface Party {
    id: number,
    name: string,
    abbreviation: string,
    description: string,
    politicians: number[],
    color: string,
    textColor: string,
    leftwing_tendency: number,
};

interface PartyWithPercentage extends Party {
    start_percent: number,
    end_percent: number,
}
interface PoliticianWithPartyId extends Politician {
    party: number;
}
interface PoliticianWithParty extends Politician {
    party: Party;
}

// important DOM things
const parties = (JSON.parse(document.querySelector("#parties")!.innerHTML) as Party[])
    .sort((a, b) => Math.sign(b.leftwing_tendency - a.leftwing_tendency));


class Plenum {
    private static instances: Plenum[] = [];

    private readonly id: number;
    private readonly politicians: PoliticianWithParty[];

    private plenum_tag: Element;
    private horiz_center: number;
    public visible: boolean;

    private constructor(id: number, plenum_tag: Element) {
        this.id = id;
        this.plenum_tag = plenum_tag;
        this.visible = false;
        (plenum_tag as any).dataset.plenumId = this.id;

        this.horiz_center = this.plenum_tag.getBoundingClientRect().width / 2;

        const datasource = "#" + plenum_tag.getAttribute("data-source") || 'plenum';


        this.politicians = ((JSON.parse(document.querySelector(datasource)!.innerHTML) || [])  as PoliticianWithPartyId[])
            .map(pol => ({ ...pol, party: parties.find(party => party.id === pol.party)! }))
            .sort((a, b) => {
                if (a.party.leftwing_tendency !== b.party.leftwing_tendency) return Math.sign(b.party.leftwing_tendency - a.party.leftwing_tendency);
                if (a.is_party_lead !== b.is_party_lead) return a.is_party_lead ? -1 : 1;
                return a.name < b.name ? -1 : 1;
            });

        Plenum.instances.push(this);
    }

    public static getInstance(plenum_tag: Element): Plenum {
        const id = parseInt(plenum_tag.getAttribute("data-plenum-id") || '');
        
        let plenum: Plenum | undefined;
        if (id) plenum = Plenum.instances.find(p => p.id === id);

        return plenum || new Plenum(Plenum.instances.length+1, plenum_tag);
    }
    
    public draw() {
        if (!this.visible) { return; }

        /* calc number of rows for plenum size */
        this.horiz_center = this.plenum_tag.getBoundingClientRect().width / 2;

        // draw them in rows
        let current_row = 1;
        let politicians = [...this.politicians];
        while (politicians.length) {
            politicians = this.draw_row(current_row, politicians, parties, true);
            current_row++;
        }

        /* resize plenum to politicians' rows */
        const max_radius = current_row*politician_diameter + initial_radius;
        this.horiz_center = max_radius;
        this.plenum_tag.innerHTML = `<div class="speakers-desk" style="left:${this.horiz_center-politician_diameter}px"></div>`;

        (this.plenum_tag as any).style.width = (max_radius * 2)  + "px";
        (this.plenum_tag as any).style.height = max_radius + "px";

        /* really draw politicians in rows */
        current_row = 1;
        politicians = [...this.politicians];
        while (politicians.length) {
            politicians = this.draw_row(current_row, politicians, parties, false);
            current_row++;
        }
    }

    private draw_row(row_num: number, politicians_with_party: PoliticianWithParty[], parties: Party[], test=false): PoliticianWithParty[] {
        const deg_to_rad = (deg: number) => deg * 2 * Math.PI / 360;
        const party_angles = this.calc_angles(row_num, parties).reduce((acc, party) => ({...acc, [party.abbreviation]: party}), {} as {[abbr: string]: PartyWithPercentage});

        // base vars
        const radius = row_num*politician_diameter + initial_radius;
        const kreisbogen = Math.PI * 2*radius * overall_angle/360;
        const num_politicians = Math.floor(kreisbogen / politician_diameter);
    
        // calc free space left & right
        const px_kreisbogen_offset = kreisbogen - (politician_diameter * num_politicians);
        const offset_percentage_kreisbogen = px_kreisbogen_offset / kreisbogen;
        const populated_kreisbogen_in_deg = overall_angle*(1-offset_percentage_kreisbogen);
    
        let remaining_politicians = [];
        let angle_in_deg = (offset_percentage_kreisbogen/2 + politician_diameter/2/kreisbogen)* populated_kreisbogen_in_deg;
        for (const politician of politicians_with_party) {
            const { start_percent, end_percent } = party_angles[politician.party.abbreviation];

            // sector of the politician's party starts later, skip empty space
            if (angle_in_deg < start_percent * populated_kreisbogen_in_deg) {
                angle_in_deg = start_percent * populated_kreisbogen_in_deg;
            }
            // sector for tor politician's party is already full, don't include them
            if (angle_in_deg >= end_percent * populated_kreisbogen_in_deg) {
                remaining_politicians.push(politician);
                continue;
            }
            // reached outer bound of angle, don't include them
            if (angle_in_deg > populated_kreisbogen_in_deg) {
                remaining_politicians.push(politician);
                continue;
            }

            if (!test) {
                // draw politician
                const angle_in_radians = deg_to_rad(angle_in_deg);
                this.plenum_tag.innerHTML += this.create_politician(
                    politician,
                    Math.cos(angle_in_radians) * radius,
                    Math.sin(angle_in_radians) * radius,
                );
            }
    
            // prep for next round
            angle_in_deg += (1/num_politicians)* populated_kreisbogen_in_deg;
        }
        return remaining_politicians;
    }

    private calc_angles(row_num: number, parties: Party[]): PartyWithPercentage[] {
        const reduced_parties = parties.filter(party => party.politicians.length);
        const total_amount_politicians = reduced_parties.reduce((acc, party) => acc + party.politicians.length, 0);
    
        // get seats in row
        const radius = row_num*politician_diameter + initial_radius;
        const kreisbogen = Math.PI * 2*radius * overall_angle/360;
        const all_seats = Math.floor(kreisbogen / politician_diameter);
        const free_seats = all_seats - reduced_parties.length;
    
        let curr_percent = 0;
        return parties.map((party) => {
            const start_percent = curr_percent;
            curr_percent = party.politicians.length ? start_percent + 1/all_seats + free_seats/all_seats*(party.politicians.length / total_amount_politicians) : start_percent;
            return {
                ...party,
                start_percent,
                end_percent: curr_percent,
            };
        });
    }

    private create_politician(politician_with_party: PoliticianWithParty, x: number, y: number): string {
        const abbr_politician = {
            ...politician_with_party,
            party: Object.entries(politician_with_party.party)
                .reduce((acc, [key, val]) => {
                    if (key === "politicians") return acc;
                    return {...acc, [key]: val};
                }, {})
            }
        let svg = "";
        switch(politician_with_party.vote) {
            case "y": svg =
                `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--!Font Awesome Free 6.6.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2024 Fonticons, Inc.-->
                    <path fill="${politician_with_party.party.textColor}" d="M464 256A208 208 0 1 0 48 256a208 208 0 1 0 416 0zM0 256a256 256 0 1 1 512 0A256 256 0 1 1 0 256z"/>
                </svg>`;
                break;
            case "n": svg =
                `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512"><!--!Font Awesome Free 6.6.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2024 Fonticons, Inc.-->
                    <path fill="${politician_with_party.party.textColor}" d="M342.6 150.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L192 210.7 86.6 105.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3L146.7 256 41.4 361.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L192 301.3 297.4 406.6c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L237.3 256 342.6 150.6z"/>
                </svg>`;
                break;
            case "e": svg =
                `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512"><!--!Font Awesome Free 6.6.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2024 Fonticons, Inc.-->
                    <path fill="${politician_with_party.party.textColor}" d="M24 0C10.7 0 0 10.7 0 24S10.7 48 24 48l8 0 0 19c0 40.3 16 79 44.5 107.5L158.1 256 76.5 337.5C48 366 32 404.7 32 445l0 19-8 0c-13.3 0-24 10.7-24 24s10.7 24 24 24l336 0c13.3 0 24-10.7 24-24s-10.7-24-24-24l-8 0 0-19c0-40.3-16-79-44.5-107.5L225.9 256l81.5-81.5C336 146 352 107.3 352 67l0-19 8 0c13.3 0 24-10.7 24-24s-10.7-24-24-24L24 0zM192 289.9l81.5 81.5C293 391 304 417.4 304 445l0 19L80 464l0-19c0-27.6 11-54 30.5-73.5L192 289.9zm0-67.9l-81.5-81.5C91 121 80 94.6 80 67l0-19 224 0 0 19c0 27.6-11 54-30.5 73.5L192 222.1z"/>
                </svg>`;
                break;
        }

        return `<button title="${politician_with_party.name || 'Name fehlt'} (${politician_with_party.genere || 'Genere fehlt'}) - ${politician_with_party.birthyear || 'Geburtsjahr fehlt'}"
            style="--color: ${ politician_with_party.party.textColor }; --bg-color: ${ politician_with_party.party.color }; left: calc(${this.horiz_center}px - var(--politician-size) / 2); top: calc(var(--politician-size) / -2); translate: ${x}px ${y}px; "
            class="politician ${ politician_with_party.is_party_lead ? 'politician--lead' : ''}"
            data-politician='${JSON.stringify(abbr_politician)}'>${svg}
        </button>`;
    }
}



function init() {
    // set css variables
    const cssRoot = document.querySelector(':root')!;
    (cssRoot as any).style.setProperty('--politician-size', `${politician_diameter}px`);
    (cssRoot as any).style.setProperty('--politician-inner-size', `80%`);

    // show/hide plenums in collapseables
    document.querySelectorAll(".plenum-collapse").forEach(btn => btn.addEventListener("click", function(e) {
        const plenum = Plenum.getInstance(document.querySelector(`${(e.target as any).dataset.bsTarget} .plenum`)!);
        plenum.visible = !plenum.visible;
        // plenum.draw(); ist handled automatically by ResizeObserver
    }))
    
    // listen to resize of plenum to paint politicians
    const plenum_observer = new ResizeObserver(entries => entries.forEach(e => {
            const plenum = Plenum.getInstance(e.target);
            if (e.target.classList.contains("plenum--main")) plenum.visible = true;
            plenum.draw();
    }));
    document.querySelectorAll(".plenum").forEach(plenum => {
        plenum_observer.observe(plenum);
    });
}
init();