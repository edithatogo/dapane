// Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
const templateForm = document.querySelector("#model-template-form");
if (templateForm) {
    const stages = [...templateForm.querySelectorAll("[data-step]")];
    const profile = templateForm.querySelector("#profile");
    const fileInput = templateForm.querySelector("#profile_file");
    const status = templateForm.querySelector("#profile-status");
    const next = templateForm.querySelector("#template-next");
    const back = templateForm.querySelector("#template-back");
    const download = templateForm.querySelector("#template-download");
    const drop = templateForm.querySelector("#profile-drop");
    let currentStage = 0;

    function showStage(index) {
        currentStage = index;
        stages.forEach((stage, stageIndex) => {
            stage.hidden = stageIndex !== index;
        });
        back.hidden = index === 0;
        next.hidden = index === stages.length - 1;
        download.hidden = !next.hidden;
        if (next.hidden) {
            const model = templateForm.elements.model.value;
            const format = templateForm.elements.format.value.toUpperCase();
            const selected = profile.value.trim() || fileInput.files.length;
            const description = selected ? "Lab profile selected." : "Standard categories.";
            templateForm.querySelector("#template-summary").textContent =
                `${model.toUpperCase()} template, ${format}. ${description}`;
        }
    }

    next.addEventListener("click", () => showStage(currentStage + 1));
    back.addEventListener("click", () => showStage(currentStage - 1));
    templateForm.addEventListener("submit", (event) => {
        if (currentStage !== stages.length - 1) {
            event.preventDefault();
            showStage(currentStage + 1);
        }
    });

    drop.hidden = false;
    drop.addEventListener("dragover", (event) => event.preventDefault());
    drop.addEventListener("drop", async (event) => {
        event.preventDefault();
        const files = event.dataTransfer.files;
        if (files.length !== 1 || files[0].size > 64 * 1024) {
            status.textContent = "Choose one JSON file of up to 64 KiB.";
            return;
        }
        try {
            const contents = await files[0].text();
            JSON.parse(contents);
            profile.value = contents;
            fileInput.value = "";
            status.textContent = "Profile loaded.";
        } catch {
            status.textContent = "Choose a readable JSON profile.";
        }
    });

    const builder = templateForm.querySelector("#profile-builder");
    builder.hidden = false;
    templateForm.querySelector("#build-profile").addEventListener("click", () => {
        const categories = Object.create(null);
        const rows = builder.querySelector("#local-categories").value.trim();
        for (const line of rows ? rows.split("\n") : []) {
            const parts = line.split(":");
            const name = parts[0].trim();
            if (parts.length !== 2 || !name || Object.hasOwn(categories, name)) {
                status.textContent = "Give each category a distinct name and subcategories.";
                return;
            }
            const subcategories = parts[1].split(",").map((item) => item.trim());
            if (subcategories.some((item) => !item)) {
                status.textContent = "Enter each subcategory name.";
                return;
            }
            categories[name] = subcategories;
        }
        const adjustments = {
            labor_multiplier: builder.querySelector("#labour-multiplier").value.trim(),
        };
        const equipment = builder.querySelector("#equipment-life");
        if (equipment.value) {
            if (!equipment.checkValidity()) {
                status.textContent = "Enter a positive whole number for equipment life.";
                return;
            }
            adjustments.equipment_depreciation_years = equipment.valueAsNumber;
        }
        profile.value = JSON.stringify({
            lab_name: builder.querySelector("#lab-name").value.trim(),
            custom_categories: categories,
            cost_adjustments: adjustments,
        }, null, 2);
        fileInput.value = "";
        status.textContent = "Profile added to this template request.";
    });
    showStage(0);
}
