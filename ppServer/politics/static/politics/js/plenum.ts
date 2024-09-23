// config
const politician_diameter = 20;
const overall_angle = 180;
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
    rightwing_tendency: number,
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
    .sort((a, b) => Math.sign(b.rightwing_tendency - a.rightwing_tendency));


class Plenum {
    private static instances: Plenum[] = [];

    private readonly id: number;
    private readonly politicians: PoliticianWithParty[];

    private plenum_tag: Element;
    private horiz_center: number;

    private constructor(id: number, plenum_tag: Element) {
        this.id = id;
        this.plenum_tag = plenum_tag;
        (plenum_tag as any).dataset.plenumId = this.id;

        this.horiz_center = this.plenum_tag.getBoundingClientRect().width / 2;

        const datasource = "#" + plenum_tag.getAttribute("data-source") || 'plenum';


        this.politicians = ((JSON.parse(document.querySelector(datasource)!.innerHTML) || [])  as PoliticianWithPartyId[])
            .map(pol => ({ ...pol, party: parties.find(party => party.id === pol.party)! }))
            .sort((a, b) => {
                if (a.party.rightwing_tendency !== b.party.rightwing_tendency) return Math.sign(b.party.rightwing_tendency - a.party.rightwing_tendency);
                if (a.is_party_lead !== b.is_party_lead) return a.is_party_lead ? -1 : 1;
                return a.name < b.name ? -1 : 1;
            });
    }

    public static getInstance(plenum_tag: Element): Plenum {
        const id = parseInt(plenum_tag.getAttribute("data-plenum-id") || '');
        
        let plenum: Plenum | undefined;
        if (id) plenum = Plenum.instances.find(p => p.id === id);

        return plenum || new Plenum(Plenum.instances.length+1, plenum_tag);
    }
    
    public draw() {
        this.horiz_center = this.plenum_tag.getBoundingClientRect().width / 2;
        this.plenum_tag.innerHTML = `<div class="speakers-desk"></div>`;
        
        // draw them in rows
        let current_row = 1;
        let politicians = [...this.politicians];
        while (politicians.length) {
            politicians = this.draw_row(current_row, politicians, parties);
            current_row++;
        }
        
        // resize plenum to politicians' placements
        const max_radius = current_row*politician_diameter + initial_radius;
        (this.plenum_tag as any).style.width = (max_radius * 2)  + "px";
        (this.plenum_tag as any).style.height = max_radius + "px";
    }

    private draw_row(row_num: number, politicians_with_party: PoliticianWithParty[], parties: Party[]): PoliticianWithParty[] {
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
            
            // draw politician
            const angle_in_radians = deg_to_rad(angle_in_deg);
            this.plenum_tag.innerHTML += this.create_politician(
                politician,
                Math.cos(angle_in_radians) * radius,
                Math.sin(angle_in_radians) * radius,
            );
    
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
            case "y": svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
                    <path fill="${politician_with_party.party.textColor}" d="M313.4 32.9c26 5.2 42.9 30.5 37.7 56.5l-2.3 11.4c-5.3 26.7-15.1 52.1-28.8 75.2l144 0c26.5 0 48 21.5 48 48c0 18.5-10.5 34.6-25.9 42.6C497 275.4 504 288.9 504 304c0 23.4-16.8 42.9-38.9 47.1c4.4 7.3 6.9 15.8 6.9 24.9c0 21.3-13.9 39.4-33.1 45.6c.7 3.3 1.1 6.8 1.1 10.4c0 26.5-21.5 48-48 48l-97.5 0c-19 0-37.5-5.6-53.3-16.1l-38.5-25.7C176 420.4 160 390.4 160 358.3l0-38.3 0-48 0-24.9c0-29.2 13.3-56.7 36-75l7.4-5.9c26.5-21.2 44.6-51 51.2-84.2l2.3-11.4c5.2-26 30.5-42.9 56.5-37.7zM32 192l64 0c17.7 0 32 14.3 32 32l0 224c0 17.7-14.3 32-32 32l-64 0c-17.7 0-32-14.3-32-32L0 224c0-17.7 14.3-32 32-32z"/>
                </svg>`; break;
            case "n": svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
                    <path fill="${politician_with_party.party.textColor}" d="M313.4 479.1c26-5.2 42.9-30.5 37.7-56.5l-2.3-11.4c-5.3-26.7-15.1-52.1-28.8-75.2l144 0c26.5 0 48-21.5 48-48c0-18.5-10.5-34.6-25.9-42.6C497 236.6 504 223.1 504 208c0-23.4-16.8-42.9-38.9-47.1c4.4-7.3 6.9-15.8 6.9-24.9c0-21.3-13.9-39.4-33.1-45.6c.7-3.3 1.1-6.8 1.1-10.4c0-26.5-21.5-48-48-48l-97.5 0c-19 0-37.5 5.6-53.3 16.1L202.7 73.8C176 91.6 160 121.6 160 153.7l0 38.3 0 48 0 24.9c0 29.2 13.3 56.7 36 75l7.4 5.9c26.5 21.2 44.6 51 51.2 84.2l2.3 11.4c5.2 26 30.5 42.9 56.5 37.7zM32 384l64 0c17.7 0 32-14.3 32-32l0-224c0-17.7-14.3-32-32-32L32 96C14.3 96 0 110.3 0 128L0 352c0 17.7 14.3 32 32 32z"/>
                </svg>`; break;
            case "e": svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512">
                    <path fill="${politician_with_party.party.textColor}" d="M342.6 150.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L192 210.7 86.6 105.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3L146.7 256 41.4 361.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L192 301.3 297.4 406.6c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L237.3 256 342.6 150.6z"/>
                </svg>`; break;
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
    
    // listen to resize of plenum to paint politicians
    const plenum_observer = new ResizeObserver(entries => entries.forEach(e => Plenum.getInstance(e.target).draw()));
    document.querySelectorAll(".plenum").forEach(plenum => {
        plenum_observer.observe(plenum);
    });
}
init();