class Console {
    /**
     * Actually log messages, with optional text-to-speech
     * @param message 
     * @param wait_ms wait after logging (for usually 0.5s)
     */
    protected async log_phenomenon_round(message: string, wait_ms: number = 500): Promise<any> {
        await new Promise(r => setTimeout(r, wait_ms));

        // log to console
        logger.log(message);


        // text to speech (if Speech Synthesis is supported)
        if (!SPEECH_ENABLED || !('speechSynthesis' in window)) { return; }

        const speaker = new SpeechSynthesisUtterance();
        const speech_ended = new Promise((resolve, _reject) => {    // eventlistener for speech end as Promise
            speaker.addEventListener("end", resolve);
        })
        
        speaker.lang = 'en';
        speaker.text = message;
        speaker.rate = 1; // (0, 10]
        window.speechSynthesis.speak(speaker);

        // wait for speech to end
        return speech_ended;
    }
}

class InquiryLogger extends Console {
    private get_order(): {phenomenon: BlockTile, number: string}[] {
        return (game_board.all().filter(tile => tile.is_phenomenon) as BlockTile[])
            .map(phenomenon => ({
                phenomenon,
                prio: phenomenon!.TYPE === TimeFissureType.TIME_LINEARRISS ? NumberPrio.LINEARRISS : NumberPrio.OTHER,
                number: phenomenon!.pos.x * GRID_HEIGHT + phenomenon!.pos.y
            }))
            .sort((a, b) => a.prio - b.prio || a.number - b.number)
            .map(({phenomenon}, i) => ({phenomenon, number: `#${i+1}: ${DEBUG ? ' (' + phenomenon.pos.x + ', ' + phenomenon.pos.y + ' ' + phenomenon.TYPE + ')' : ''} `}))
    }

    public async run(
        command: InquiryCommand,
        details?: string
    ) {
        if (command === InquiryCommand.HELP1 || command === InquiryCommand.HELP) {
            for (const comm of Object.values(InquiryCommand)) {
                await this.log_phenomenon_round(comm);
            }
        }

        if (command === InquiryCommand.HELP2 || command === InquiryCommand.HELP) {
            for (const comm of Object.values(Command)) {
                await this.log_phenomenon_round(comm);
            }
        }

        const phemonena = this.get_order();

        if (command === InquiryCommand.STUFE) {

            const res = /^([<>=])\s*(\d+)$/.exec(details || "");
            if (res?.length !== 3) {
                logger.error(`Das Format ist '${command} operator stufe', wobei der Operator '<', '>' oder '=' sein kann`);
                return;
            }
            const operation: "<" | ">" | "=" = res[1] as any;
            const stufe = parseInt(res[2]!);
            const test = (phenomenon_stufe: number): boolean =>  {
                switch (operation) {
                    case "<": return phenomenon_stufe < stufe;
                    case ">": return phenomenon_stufe > stufe;
                    case "=": return phenomenon_stufe === stufe;
                }
            }

            logger.debug(operation, stufe)

            for (const {phenomenon, number} of phemonena) {
                await this.log_phenomenon_round(`${number}${!!phenomenon.stufe && test(phenomenon.stufe)}`);
            }
        }

        if (command === InquiryCommand.TYPE) {
            
            if (!["RR", "ZR", "ZA"].includes(details || "")) {
                logger.error(`Das Format ist '${command} ?', wobei ? 'RR' (Raumriss), 'ZR' (Zeitriss) oder 'ZA' (Zeitanomalie) sein kann`);
                return;
            }

            const test = (phenomenon_type: TileType): boolean =>  {
                switch (details as "RR" | "ZR" | "ZA") {
                    case "RR": return Object.values(SpaceFissureType).includes(phenomenon_type as any);
                    case "ZR": return Object.values(TimeFissureType).includes(phenomenon_type as any);
                    case "ZA": return Object.values(AnomalyType).includes(phenomenon_type as any);
                }
            }
            logger.debug(details)

            for (const {phenomenon, number} of phemonena) {
                await this.log_phenomenon_round(`${number}${test(phenomenon.TYPE)}`);
            }
        }

        if (command === InquiryCommand.RESPONSE) {
            const phenomenon = phemonena.find(({number}) => number.startsWith(details || ""));
            if (!/^#\d+$/.test(details || "") || !phenomenon) {
                logger.error(`${command} ${details} ist unbekannt. Das Format ist ${command} #?, wobei ? die Nummer des Phänomens ist`);
                return;
            }
            logger.debug(details);

            // TODO change answer to something else than 'true'?
            await this.log_phenomenon_round(`${phenomenon.number}${true}`);
        }

        if (command === InquiryCommand.SPLITS) {
            const phenomenon = phemonena.find(({number}) => number.startsWith(details || ""));
            if (!/^#\d+$/.test(details || "") || !phenomenon) {
                logger.error(`${command} ${details} ist unbekannt. Das Format ist ${command} #?, wobei ? die Nummer des Phänomens ist`);
                return;
            }
            const test = (p: BlockTile): boolean => p.TYPE === TimeFissureType.TIME_LINEARRISS && (p as Linearriss).splits > 0;

            logger.debug(details);

            await this.log_phenomenon_round(`${phenomenon.number}${test(phenomenon.phenomenon)}`);
        }

        if (command === InquiryCommand.SPLITN) {
            const phenomenon = phemonena.find(({number}) => number.startsWith(details || ""));
            if (!/^#\d+$/.test(details || "") || !phenomenon) {
                logger.error(`${command} ${details} ist unbekannt. Das Format ist ${command} #?, wobei ? die Nummer des Phänomens ist`);
                return;
            }
            const test = (p: BlockTile): number => p.TYPE === TimeFissureType.TIME_LINEARRISS ? (p as Linearriss).splits : 0;

            logger.debug(details);

            await this.log_phenomenon_round(`${phenomenon.number}${test(phenomenon.phenomenon)}`);
        }
    }
}

class Logger extends Console {
    private round_answers: {
        order_prio: OrderPrio,
        number_prio: NumberPrio,
        displayed_number: {
            number: number | null,
            postfix: "?" | "",
        },
        id: number,
        messages: ((prev_msg: string) => string)[]
    }[] = [];


    /**
     * Register messages to log to the console
     * @param tile      the tile speaking
     * @param messages   the message it says
     */
    public register_round_answer(tile: BlockTile, ...messages: string[]): void {
        let order = OrderPrio.OTHER;
        let number = NumberPrio.OTHER;
        switch (tile.TYPE) {
            case TimeFissureType.TIME_LINEARRISS: order = OrderPrio.LINEARRISS; number = NumberPrio.LINEARRISS; break;
            case TimeFissureType.TIME_TIMELAGGER: order = OrderPrio.TIMELAGGER; break;
            case TimeFissureType.TIME_RUNNER: order = OrderPrio.RUNNER;
        }
        
        this.round_answers.push({
            order_prio: order,
            number_prio: number,
            id: tile.pos.x * GRID_HEIGHT + tile.pos.y,
            displayed_number: {
                number: null,
                postfix: tile instanceof TimeFissure && tile.is_covered_as_liniendeletion ? "?" : "",
            },
            messages: messages.map(msg => {
                const debug = DEBUG ? `(${tile.pos.x}, ${tile.pos.y}: ${tile.TYPE}) ` : "";
                return tile.TYPE === TimeFissureType.TIME_TIMELAGGER ?
                    (prev_msg) => `${debug}${prev_msg} ${msg}` :
                    () => `${debug}${msg}`
            }),
        });
    }


    public async log_round_answers() {
        // sort logs by number to assign numbers
        this.round_answers = this.round_answers
            .sort((a, b) => a.number_prio - b.number_prio || a.id - b.id)
            .map((log, i) => ({...log, displayed_number: { ...log.displayed_number, number: i+1 }}));


        // sort logs by id
        this.round_answers = this.round_answers.sort((a, b) => a.order_prio - b.order_prio || a.id - b.id);

        // print them
        let prev_msg = "";
        while (this.round_answers.length) {
            const log = this.round_answers.shift()!;

            for (const msg of log.messages) {
                const answer = msg(prev_msg);
                prev_msg = answer;
                const message = `#${log.displayed_number.number}${log.displayed_number.postfix}: ${answer}`;
                await logger.log_phenomenon_round(message, log.order_prio === OrderPrio.TIMELAGGER ? 3000 : 500);
            }
        }
    }

    public debug(...data: any[]): void {
        if (DEBUG) {
            console.debug(...data);
        }
    }
    public info(...data: any[]): void {
        if (DEBUG) {
            console.info(...data);
        }
    }
    public log(...data: any[]): void {
        const line = document.createElement("span");
        line.innerHTML = data.join(" ");
        line.classList.add("line");
        document.querySelector(".output")!.appendChild(line);
    }
    public warn(...data: any[]): void {
        const line = document.createElement("span");
        line.innerHTML = data.join(" ");
        line.classList.add("line", "line--warn");
        document.querySelector(".output")!.appendChild(line);
    }
    public error(...data: any[]): void {
        const line = document.createElement("span");
        line.innerHTML = data.join(" ");
        line.classList.add("line", "line--error");
        document.querySelector(".output")!.appendChild(line);
    }
}
