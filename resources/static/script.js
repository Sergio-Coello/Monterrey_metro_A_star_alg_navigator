document.addEventListener("DOMContentLoaded", () => {
    const themeSelector = document.getElementById("themeSelector");
    const root = document.documentElement;
    const savedTheme = localStorage.getItem("metrorrey-theme");
    const currentTheme = savedTheme === "light" ? "light" : "dark";

    root.setAttribute("data-theme", currentTheme);
    if (themeSelector) {
        themeSelector.value = currentTheme;
        themeSelector.addEventListener("change", () => {
            root.setAttribute("data-theme", themeSelector.value);
            localStorage.setItem("metrorrey-theme", themeSelector.value);
        });
    }

    const originInput = document.getElementById("origin");
    const destinationInput = document.getElementById("destination");
    const swapButton = document.getElementById("swapStations");
    const stationData = document.getElementById("stationNames");
    const allStations = stationData ? JSON.parse(stationData.textContent) : [];
    const normalize = value => value.normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase()
        .replace(/[^a-z0-9]/g, "");

    function setupStationPicker(input, menu) {
        if (!input || !menu) return;

        let activeIndex = -1;

        function closeMenu() {
            menu.hidden = true;
            input.setAttribute("aria-expanded", "false");
            input.removeAttribute("aria-activedescendant");
            activeIndex = -1;
        }

        function chooseStation(name) {
            input.value = name;
            input.dispatchEvent(new Event("change", {bubbles: true}));
            closeMenu();
        }

        function renderOptions() {
            const query = normalize(input.value);
            const matches = query
                ? allStations.filter(name => normalize(name).includes(query))
                : allStations;

            menu.replaceChildren();
            activeIndex = -1;

            if (matches.length === 0) {
                const empty = document.createElement("div");
                empty.className = "station-options-empty";
                empty.textContent = "No se encontraron estaciones";
                menu.appendChild(empty);
            } else {
                matches.forEach((name, index) => {
                    const option = document.createElement("button");
                    option.type = "button";
                    option.className = "station-option";
                    option.id = `${menu.id}-option-${index}`;
                    option.role = "option";
                    option.textContent = name;
                    option.addEventListener("click", () => chooseStation(name));
                    menu.appendChild(option);
                });
            }

            menu.hidden = false;
            input.setAttribute("aria-expanded", "true");
        }

        function highlightOption(index) {
            const options = menu.querySelectorAll(".station-option");
            if (!options.length) return;
            activeIndex = (index + options.length) % options.length;
            options.forEach((option, optionIndex) => {
                option.classList.toggle("active", optionIndex === activeIndex);
            });
            input.setAttribute(
                "aria-activedescendant", options[activeIndex].id
            );
            options[activeIndex].scrollIntoView({block: "nearest"});
        }

        input.addEventListener("focus", renderOptions);
        input.addEventListener("input", renderOptions);
        input.addEventListener("keydown", event => {
            if (event.key === "ArrowDown") {
                event.preventDefault();
                if (menu.hidden) renderOptions();
                highlightOption(activeIndex + 1);
            } else if (event.key === "ArrowUp" && !menu.hidden) {
                event.preventDefault();
                highlightOption(activeIndex - 1);
            } else if (event.key === "Enter" && !menu.hidden && activeIndex >= 0) {
                event.preventDefault();
                chooseStation(menu.querySelectorAll(".station-option")[activeIndex].textContent);
            } else if (event.key === "Escape") {
                closeMenu();
            }
        });

        document.addEventListener("pointerdown", event => {
            if (!input.parentElement.contains(event.target)) closeMenu();
        });
    }

    setupStationPicker(
        originInput, document.getElementById("originOptions")
    );
    setupStationPicker(
        destinationInput, document.getElementById("destinationOptions")
    );

    if (swapButton && originInput && destinationInput) {
        swapButton.addEventListener("click", () => {
            const temporary = originInput.value;
            originInput.value = destinationInput.value;
            destinationInput.value = temporary;
        });
    }

    // Coordenadas aproximadas de cada estación sobre la imagen original
    // (1600 x 1004). Los nodos de transbordo comparten coordenadas.
    const coordinates = {
        "Talleres": [475, 329],
        "San Bernabé": [519, 368],
        "Unidad Modelo": [569, 409],
        "Aztlán": [608, 444],
        "Penitenciaría": [690, 501],
        "Alfonso Reyes": [691, 551],
        "Mitras": [691, 601],
        "Simón Bolívar": [691, 663],
        "Hospital": [691, 733],
        "Edison": [745, 736],
        "Central": [803, 736],
        "Cuauhtémoc": [862, 743],
        "Del Golfo": [937, 768],
        "Félix U. Gómez": [1010, 782],
        "Parque Fundidora": [1084, 808],
        "Y Griega": [1157, 839],
        "Eloy Cavazos": [1234, 864],
        "Lerdo de Tejada": [1294, 862],
        "Exposición": [1358, 855],
        "Sendero": [1008, 210],
        "Santiago Tapia": [1003, 263],
        "San Nicolás": [979, 327],
        "Anáhuac": [955, 410],
        "Universidad": [931, 469],
        "Niños Héroes": [906, 537],
        "Regina": [887, 606],
        "General Anaya": [864, 672],
        "Alameda": [861, 790],
        "Fundadores": [870, 915],
        "Padre Mier": [873, 958],
        "General I. Zaragoza": [916, 920],
        "Santa Lucía": [962, 920],
        "Colonia Obrera": [966, 853],
        "Metalúrgicos": [1022, 714],
        "Moderna": [1020, 665],
        "Ruiz Cortines": [1093, 614],
        "Los Ángeles": [1139, 579],
        "Hospital Metropolitano": [1182, 544]
    };

    const svg = document.getElementById("metroOverlay");
    const routeDataElement = document.getElementById("metroRouteData");
    if (!svg || !routeDataElement) return;

    let routeData = {nodes: [], lines: []};
    try {
        routeData = JSON.parse(routeDataElement.textContent);
    } catch (error) {
        console.error("No se pudieron leer los datos de la ruta", error);
    }

    const colors = {
        L1: "#f5c518",
        L2: "#279b50",
        L3: "#ef5735",
        transfer: "#f29bc2"
    };

    const stationName = node => node.replace(/ L[123]$/, "");
    const makeSvg = (tag, attributes) => {
        const element = document.createElementNS(
            "http://www.w3.org/2000/svg", tag
        );
        Object.entries(attributes).forEach(([key, value]) => {
            element.setAttribute(key, value);
        });
        svg.appendChild(element);
        return element;
    };

    const nodes = routeData.nodes || [];
    const lines = routeData.lines || [];

    if (nodes.length > 1) {
        const trainPoints = [];

        nodes.slice(0, -1).forEach((node, index) => {
            const nextNode = nodes[index + 1];
            const from = coordinates[stationName(node)];
            const to = coordinates[stationName(nextNode)];
            if (!from || !to || stationName(node) === stationName(nextNode)) {
                return;
            }

            if (!trainPoints.length) trainPoints.push(from);
            trainPoints.push(to);

            const line = lines[index] || "transfer";
            makeSvg("line", {
                x1: from[0], y1: from[1],
                x2: to[0], y2: to[1],
                class: "route-segment",
                stroke: colors[line] || colors.transfer
            });
        });

        nodes.forEach((node, index) => {
            const name = stationName(node);
            const point = coordinates[name];
            if (!point) return;

            const isTransfer = index > 0 &&
                stationName(nodes[index - 1]) === name;
            const markerClass = isTransfer ? "route-marker transfer" :
                index === 0 ? "route-marker origin" :
                index === nodes.length - 1 ? "route-marker destination" :
                "route-marker";

            makeSvg("circle", {
                cx: point[0], cy: point[1],
                r: isTransfer ? 13 : 9,
                class: markerClass
            });
        });

        if (trainPoints.length > 1) {
            const motionPath = trainPoints.map((point, index) =>
                `${index === 0 ? "M" : "L"} ${point[0]} ${point[1]}`
            ).join(" ");
            const train = makeSvg("circle", {
                r: 8,
                class: "train-marker"
            });
            const movement = document.createElementNS(
                "http://www.w3.org/2000/svg", "animateMotion"
            );
            movement.setAttribute("path", motionPath);
            movement.setAttribute("dur", "8s");
            movement.setAttribute("repeatCount", "indefinite");
            train.appendChild(movement);
        }
    }
});
