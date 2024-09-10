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
};
interface Party {
    name: string,
    abbreviation: string,
    description: string,
    politicians: Politician[],
    color: string,
    rightwing_tendency: number,
};

interface PartyWithPercentage extends Party {
    start_percent: number,
    end_percent: number,
}
interface PoliticianWithParty extends Politician {
    party: Party;
}

// important DOM things
const parties = (JSON.parse(document.querySelector("#parties")!.innerHTML) as Party[])
    .map(party => ({
        ...party,
        politicians: (party.politicians || []).sort((a, b) => {
            if (a.is_party_lead !== b.is_party_lead) return a.is_party_lead ? -1 : 1;
            return a.name < b.name ? -1 : 1;
        })
    }))
    .sort((a, b) => Math.sign(b.rightwing_tendency - a.rightwing_tendency));

init();


function init() {
    // set css variables
    const cssRoot = document.querySelector(':root')!;
    (cssRoot as any).style.setProperty('--politician-size', `${politician_diameter}px`);
    (cssRoot as any).style.setProperty('--politician-inner-size', `80%`);
    
    // listen to resize of plenum to paint politicians
    const plenum_observer = new ResizeObserver(entries => entries.forEach(e => Plenum.getInstance(e.target).draw(parties)));
    document.querySelectorAll(".plenum").forEach(plenum => plenum_observer.observe(plenum));
}


class Plenum {
    private static instances: Plenum[] = [];

    private readonly id: number;
    private plenum_tag: Element;
    private horiz_center: number;

    private constructor(id: number, plenum_tag: Element) {
        this.id = id;
        this.plenum_tag = plenum_tag;
        (plenum_tag as any).dataset.plenumId = this.id;

        this.horiz_center = this.plenum_tag.getBoundingClientRect().width / 2;
    }

    public static getInstance(plenum_tag: Element): Plenum {
        const id = parseInt(plenum_tag.getAttribute("data-plenum-id") || '');
        
        let plenum: Plenum | undefined;
        if (id) plenum = Plenum.instances.find(p => p.id === id);

        return plenum || new Plenum(Plenum.instances.length+1, plenum_tag);
    }
    
    public draw(parties: Party[]) {
        this.horiz_center = this.plenum_tag.getBoundingClientRect().width / 2;
        this.plenum_tag.innerHTML = `<div class="speakers-desk"></div>`;
        
        // prepare politicians
        let politicians = parties.reduce((acc, party) => {
            return [...acc, ...party.politicians.map(pol => ({...pol, party}))];
        }, [] as PoliticianWithParty[]);
        
        // draw them in rows
        let current_row = 1;
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
        return `<button title="${politician_with_party.party.name} (${politician_with_party.party.abbreviation})"
            style="--color: ${ politician_with_party.party.color }; left: calc(${this.horiz_center}px - var(--politician-size) / 2); top: calc(var(--politician-size) / -2); translate: ${x}px ${y}px; "
            class="politician ${ politician_with_party.is_party_lead ? 'politician--lead' : ''}"
            data-politician='${JSON.stringify(abbr_politician)}'>
        </button>`;
    }
}