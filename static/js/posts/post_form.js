document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("file-input");
    const list = document.getElementById("draft-files");
    const form = document.querySelector("form");

    let draftFiles = [];

    input.addEventListener("change", () => {
        const file = input.files[0];
        if (!file) return;

        draftFiles.push(file);
        input.value = "";
        render();
    });

    function render() {
        list.innerHTML = "";

        draftFiles.forEach((file, index) => {
            const item = document.createElement("div");
            item.className = "d-flex justify-content-between align-items-center border rounded p-2 mb-2";

            item.innerHTML = `
                <div class="text-truncate">
                    📎 ${file.name}
                    <small class="text-muted">(${(file.size/1024/1024).toFixed(2)} MB)</small>
                </div>
                <button type="button" class="btn btn-sm btn-outline-danger">✕</button>
            `;

            item.querySelector("button").onclick = () => {
                draftFiles.splice(index, 1);
                render();
            };

            list.appendChild(item);
        });
    }

    form.addEventListener("submit", () => {
        const dt = new DataTransfer();
        draftFiles.forEach(f => dt.items.add(f));
        input.files = dt.files;
    });
});
document.querySelectorAll(".remove-current-file").forEach(btn => {
    btn.addEventListener("click", () => {
        const container = btn.closest(".file-item");
        const fileId = container.dataset.fileId;

        const input = document.createElement("input");
        input.type = "hidden";
        input.name = "delete_files";
        input.value = fileId;

        document.querySelector("form").appendChild(input);

        container.remove();
    });
});
