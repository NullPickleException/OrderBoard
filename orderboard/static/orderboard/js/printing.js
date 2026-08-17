document.addEventListener("DOMContentLoaded", function () {
    // =========================================================================
    // ELEMENTS
    // =========================================================================
    const checkboxes = document.querySelectorAll(".shipment-checkbox");
    const shipmentItems = document.querySelectorAll(".shipment-selection-item");
    const selectAllButton = document.getElementById("select-all-button");
    const clearAllButton = document.getElementById("clear-all-button");
    const selectVisibleButton = document.getElementById("select-visible-button");
    const clearVisibleButton = document.getElementById("clear-visible-button");
    const printButton = document.getElementById("print-button");
    const pdfButton = document.getElementById("pdf-button");
    const selectedCount = document.getElementById("selected-count");
    const preview = document.getElementById("print-preview");
    const emptyPreview = document.getElementById("empty-preview");
    const searchInput = document.getElementById("shipment-search");
    const statusFilter = document.getElementById("shipment-status");
    const noShipmentsFound = document.getElementById("no-shipments-found");
    const senderName = document.getElementById("sender-name");
    const senderPhone = document.getElementById("sender-phone");
    const senderAddress = document.getElementById("sender-address");
    const labelsPerPageSelect = document.getElementById("labels-per-page");
    const fontSizeInput = document.getElementById("font-size-input");
    const layoutSwap = document.getElementById("layout-swap");
    const imageUpload = document.getElementById("image-upload");
    const orientationSelect = document.getElementById("orientation");
    
    let customImageData = null;

    // =========================================================================
    // LOCALSTORAGE HELPERS
    // =========================================================================
    
    const STORAGE_KEY = "orderboard_print_settings";
    
    function loadSettings() {
        try {
            const saved = localStorage.getItem(STORAGE_KEY);
            if (saved) {
                return JSON.parse(saved);
            }
        } catch (e) {
            console.warn("Failed to load settings:", e);
        }
        return null;
    }
    
    function saveSettings() {
        try {
            const settings = {
                senderName: senderName ? senderName.value : "",
                senderPhone: senderPhone ? senderPhone.value : "",
                senderAddress: senderAddress ? senderAddress.value : "",
                labelsPerPage: labelsPerPageSelect ? labelsPerPageSelect.value : "6",
                fontSize: fontSizeInput ? fontSizeInput.value : "10",
                layoutMode: layoutSwap ? layoutSwap.value : "normal",
                orientation: orientationSelect ? orientationSelect.value : "portrait",
                customImage: customImageData
            };
            localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
        } catch (e) {
            console.warn("Failed to save settings:", e);
        }
    }
    
    function applySettings() {
        const saved = loadSettings();
        if (!saved) return;
        
        if (saved.senderName && senderName) senderName.value = saved.senderName;
        if (saved.senderPhone && senderPhone) senderPhone.value = saved.senderPhone;
        if (saved.senderAddress && senderAddress) senderAddress.value = saved.senderAddress;
        if (saved.labelsPerPage && labelsPerPageSelect) labelsPerPageSelect.value = saved.labelsPerPage;
        if (saved.fontSize && fontSizeInput) fontSizeInput.value = saved.fontSize;
        if (saved.layoutMode && layoutSwap) layoutSwap.value = saved.layoutMode;
        if (saved.orientation && orientationSelect) orientationSelect.value = saved.orientation;
        if (saved.customImage) customImageData = saved.customImage;
    }

    // =========================================================================
    // LABELS PER PAGE
    // =========================================================================
    function getLabelsPerPage() {
        if (!labelsPerPageSelect) return 6;
        const value = parseInt(labelsPerPageSelect.value, 10);
        return [4, 5, 6, 7, 8].includes(value) ? value : 6;
    }

    function getLabelRows(labelsPerPage) {
        if (labelsPerPage === 4) return 2;
        if (labelsPerPage === 5) return 3;
        if (labelsPerPage === 6) return 3;
        if (labelsPerPage === 7) return 4;
        if (labelsPerPage === 8) return 4;
        return 3;
    }

    function getLabelColumns(labelsPerPage) {
        return 2;
    }

    function getFontSizePx() {
        if (!fontSizeInput) return 10;
        const value = parseFloat(fontSizeInput.value);
        return isNaN(value) ? 10 : Math.min(Math.max(value, 6), 20);
    }

    function getLayoutMode() {
        if (!layoutSwap) return "normal";
        return layoutSwap.value;
    }

    function getOrientation() {
        if (!orientationSelect) return "portrait";
        return orientationSelect.value;
    }

    // =========================================================================
    // PHONE
    // =========================================================================
    function normalizeDigits(value) {
        if (!value) return "";
        return String(value)
            .replace(/[۰-۹]/g, function (digit) {
                return String("۰۱۲۳۴۵۶۷۸۹".indexOf(digit));
            })
            .replace(/[٠-٩]/g, function (digit) {
                return String("٠١٢٣٤٥٦٧٨٩".indexOf(digit));
            });
    }

    function formatPhone(value) {
        value = normalizeDigits(value);
        let digits = value.replace(/\D/g, "");
        if (digits.startsWith("98")) {
            digits = "0" + digits.substring(2);
        }
        if (digits.length === 11 && digits.startsWith("09")) {
            return digits.substring(0, 4) + " " + digits.substring(4, 7) + " " + digits.substring(7);
        }
        return value;
    }

    // =========================================================================
    // HTML ESCAPING
    // =========================================================================
    function escapeHtml(value) {
        if (value === null || value === undefined) return "";
        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // =========================================================================
    // SELECTION
    // =========================================================================
    function getSelectedCheckboxes() {
        return Array.from(checkboxes).filter(checkbox => checkbox.checked);
    }

    function updateSelectionState() {
        const selected = getSelectedCheckboxes();
        const count = selected.length;
        if (selectedCount) selectedCount.textContent = count + " selected";
        const hasSelection = count > 0;
        if (printButton) printButton.disabled = !hasSelection;
        if (pdfButton) pdfButton.disabled = !hasSelection;
        renderPreview();
    }

    // =========================================================================
    // SHIPMENT DATA
    // =========================================================================
    function getShipmentFromCheckbox(checkbox) {
        return {
            title: checkbox.dataset.title || "",
            customer: checkbox.dataset.customer || "",
            recipient: checkbox.dataset.recipient || "",
            phone: checkbox.dataset.phone || "",
            address: checkbox.dataset.address || "",
            postalCode: checkbox.dataset.postalCode || "",
            trackingId: checkbox.dataset.trackingId || ""
        };
    }

    // =========================================================================
    // FILTERING
    // =========================================================================
    function shipmentMatchesFilter(item) {
        const checkbox = item.querySelector(".shipment-checkbox");
        if (!checkbox) return false;
        const search = searchInput ? searchInput.value.trim().toLowerCase() : "";
        const status = statusFilter ? statusFilter.value : "active";
        if (search) {
            const searchableText = (item.dataset.search || "")
                .replace(/\s+/g, " ")
                .trim()
                .toLowerCase();
            if (!searchableText.includes(search)) return false;
        }
        const shipmentStatus = checkbox.dataset.status;
        if (status === "active") {
            if (shipmentStatus === "delivered") return false;
        } else if (status !== "all") {
            if (shipmentStatus !== status) return false;
        }
        return true;
    }

    function updateShipmentList() {
        let visibleCount = 0;
        shipmentItems.forEach(function (item) {
            const visible = shipmentMatchesFilter(item);
            item.style.display = visible ? "flex" : "none";
            if (visible) visibleCount++;
        });
        if (noShipmentsFound) {
            noShipmentsFound.style.display = visibleCount === 0 ? "block" : "none";
        }
    }

    // =========================================================================
    // CREATE LABEL
    // =========================================================================
    function createLabel(shipment) {
        const title = escapeHtml(shipment.title);
        const recipient = escapeHtml(shipment.recipient);
        const address = escapeHtml(shipment.address || "-");
        const postalCode = escapeHtml(normalizeDigits(shipment.postalCode || "-"));
        const phone = escapeHtml(formatPhone(shipment.phone));
        const trackingId = escapeHtml(normalizeDigits(shipment.trackingId || ""));
        const currentSenderName = escapeHtml(senderName ? senderName.value.trim() : "");
        const currentSenderPhone = escapeHtml(senderPhone ? formatPhone(senderPhone.value.trim()) : "");
        const currentSenderAddress = escapeHtml(senderAddress ? senderAddress.value.trim() : "");
        const fontSizePx = getFontSizePx();
        const layoutMode = getLayoutMode();
        const orientation = getOrientation();

        const label = document.createElement("article");
        label.className = "shipping-label layout-" + layoutMode + " orientation-" + orientation;
        label.style.setProperty("--font-size-px", fontSizePx + "px");
        
        const senderBox = `
            <div class="label-box sender-box">
                <div class="label-box-title">فرستنده</div>
                <div class="label-info-row">
                    <span class="label-caption">نام:</span>
                    <span class="label-value">${currentSenderName || "-"}</span>
                </div>
                <div class="label-info-row">
                    <span class="label-caption">شماره:</span>
                    <span class="label-value" dir="ltr">${currentSenderPhone || "-"}</span>
                </div>
                <div class="label-info-row">
                    <span class="label-caption">آدرس:</span>
                    <span class="label-value">${currentSenderAddress || "-"}</span>
                </div>
            </div>`;
        
        const imageBox = customImageData ? `
            <div class="label-box image-box">
                <img src="${customImageData}" alt="Custom Image">
            </div>` : `
            <div class="label-box image-box">
                <div class="image-placeholder"></div>
            </div>`;

        const receiverBox = `
            <div class="label-box receiver-box">
                <div class="label-box-title">گیرنده</div>
                <div class="label-info-row">
                    <span class="label-caption">نام:</span>
                    <span class="label-value">${recipient || "-"}</span>
                </div>
                <div class="label-info-row">
                    <span class="label-caption">شماره:</span>
                    <span class="label-value" dir="ltr">${phone || "-"}</span>
                </div>
                <div class="label-info-row">
                    <span class="label-caption">آدرس:</span>
                    <span class="label-value">${address}</span>
                </div>
                <div class="label-info-row">
                    <span class="label-caption">کد پستی:</span>
                    <span class="label-value" dir="ltr">${postalCode}</span>
                </div>
                ${trackingId ? `
                    <div class="label-info-row">
                        <span class="label-caption">کد رهگیری:</span>
                        <span class="label-value" dir="ltr">${trackingId}</span>
                    </div>` : ""}
            </div>`;

        if (layoutMode === "no-image") {
            label.innerHTML = `
                ${senderBox}
                ${receiverBox}`;
        } else {
            label.innerHTML = `
                <div class="label-top-section">
                    ${layoutMode === "swapped" ? imageBox + senderBox : senderBox + imageBox}
                </div>
                ${receiverBox}`;
        }
        
        return label;
    }

    // =========================================================================
    // CREATE A4 PAGE
    // =========================================================================
    function createPrintPage(labelsPerPage, orientation) {
        const page = document.createElement("section");
        page.className = "print-page labels-" + labelsPerPage + " orientation-" + orientation;
        page.style.setProperty("--label-rows", getLabelRows(labelsPerPage));
        page.style.setProperty("--label-columns", getLabelColumns(labelsPerPage));
        return page;
    }

    // =========================================================================
    // RENDER PREVIEW
    // =========================================================================
    function renderPreview() {
        if (!preview) return;
        const selected = getSelectedCheckboxes();
        preview.querySelectorAll(".print-page").forEach(page => page.remove());

        if (selected.length === 0) {
            if (emptyPreview) emptyPreview.style.display = "flex";
            return;
        }
        if (emptyPreview) emptyPreview.style.display = "none";

        const labelsPerPage = getLabelsPerPage();
        const orientation = getOrientation();
        let currentPage = null;

        selected.forEach(function (checkbox, index) {
            if (index % labelsPerPage === 0) {
                currentPage = createPrintPage(labelsPerPage, orientation);
                preview.appendChild(currentPage);
            }
            const shipment = getShipmentFromCheckbox(checkbox);
            currentPage.appendChild(createLabel(shipment));
        });
    }

    // =========================================================================
    // IMAGE UPLOAD
    // =========================================================================
    if (imageUpload) {
        imageUpload.addEventListener("change", function (event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    customImageData = e.target.result;
                    saveSettings();
                    renderPreview();
                };
                reader.readAsDataURL(file);
            } else {
                customImageData = null;
                saveSettings();
                renderPreview();
            }
        });
    }

    // =========================================================================
    // ORIENTATION CHANGE
    // =========================================================================
    if (orientationSelect) {
        orientationSelect.addEventListener("change", function() {
            saveSettings();
            renderPreview();
        });
    }

    // =========================================================================
    // FONT SIZE INPUT
    // =========================================================================
    if (fontSizeInput) {
        fontSizeInput.addEventListener("input", renderPreview);
        fontSizeInput.addEventListener("change", function() {
            saveSettings();
            renderPreview();
        });
    }

    // =========================================================================
    // LABELS PER PAGE
    // =========================================================================
    if (labelsPerPageSelect) {
        labelsPerPageSelect.addEventListener("change", function() {
            saveSettings();
            renderPreview();
        });
    }

    // =========================================================================
    // LAYOUT SWAP
    // =========================================================================
    if (layoutSwap) {
        layoutSwap.addEventListener("change", function() {
            saveSettings();
            renderPreview();
        });
    }

    // =========================================================================
    // SELECT ALL
    // =========================================================================
    if (selectAllButton) {
        selectAllButton.addEventListener("click", function () {
            checkboxes.forEach(checkbox => { checkbox.checked = true; });
            updateSelectionState();
        });
    }

    // =========================================================================
    // CLEAR ALL
    // =========================================================================
    if (clearAllButton) {
        clearAllButton.addEventListener("click", function () {
            checkboxes.forEach(checkbox => { checkbox.checked = false; });
            updateSelectionState();
        });
    }

    // =========================================================================
    // SELECT VISIBLE
    // =========================================================================
    if (selectVisibleButton) {
        selectVisibleButton.addEventListener("click", function () {
            shipmentItems.forEach(function (item) {
                if (item.style.display !== "none") {
                    const checkbox = item.querySelector(".shipment-checkbox");
                    if (checkbox) checkbox.checked = true;
                }
            });
            updateSelectionState();
        });
    }

    // =========================================================================
    // CLEAR VISIBLE
    // =========================================================================
    if (clearVisibleButton) {
        clearVisibleButton.addEventListener("click", function () {
            shipmentItems.forEach(function (item) {
                if (item.style.display !== "none") {
                    const checkbox = item.querySelector(".shipment-checkbox");
                    if (checkbox) checkbox.checked = false;
                }
            });
            updateSelectionState();
        });
    }

    // =========================================================================
    // CHECKBOXES
    // =========================================================================
    checkboxes.forEach(function (checkbox) {
        checkbox.addEventListener("change", updateSelectionState);
    });

    // =========================================================================
    // SEARCH
    // =========================================================================
    if (searchInput) {
        searchInput.addEventListener("input", updateShipmentList);
    }

    // =========================================================================
    // STATUS FILTER
    // =========================================================================
    if (statusFilter) {
        statusFilter.addEventListener("change", updateShipmentList);
    }

    // =========================================================================
    // SENDER LIVE PREVIEW + SAVE
    // =========================================================================
    if (senderName) {
        senderName.addEventListener("input", renderPreview);
        senderName.addEventListener("change", saveSettings);
    }
    if (senderPhone) {
        senderPhone.addEventListener("input", renderPreview);
        senderPhone.addEventListener("change", saveSettings);
    }
    if (senderAddress) {
        senderAddress.addEventListener("input", renderPreview);
        senderAddress.addEventListener("change", saveSettings);
    }

    // =========================================================================
    // PRINT
    // =========================================================================
    if (printButton) {
        printButton.addEventListener("click", function () {
            if (getSelectedCheckboxes().length === 0) return;
            saveSettings();
            renderPreview();
            setTimeout(function () { window.print(); }, 100);
        });
    }

    // =========================================================================
    // EXPORT PDF
    // =========================================================================
    if (pdfButton) {
        pdfButton.addEventListener("click", async function () {
            const selected = getSelectedCheckboxes();
            if (selected.length === 0) return;
            
            if (typeof html2pdf === "undefined") {
                alert("PDF generator is not available. Please check your internet connection and reload the page.");
                return;
            }

            saveSettings();
            renderPreview();
            pdfButton.disabled = true;
            const originalText = pdfButton.textContent;
            pdfButton.textContent = "Generating PDF...";

            try {
                const orientation = getOrientation();
                const opt = {
                    margin: 0,
                    filename: 'shipping-labels.pdf',
                    image: { type: 'jpeg', quality: 0.98 },
                    html2canvas: { 
                        scale: 2,
                        useCORS: true,
                        backgroundColor: '#ffffff'
                    },
                    jsPDF: { 
                        unit: 'mm', 
                        format: 'a4', 
                        orientation: orientation === "landscape" ? "landscape" : "portrait"
                    },
                    pagebreak: { 
                        mode: ['avoid-all', 'css', 'legacy']
                    }
                };

                await html2pdf().from(preview).set(opt).save();

            } catch (error) {
                console.error("Failed to generate PDF:", error);
                alert("Could not generate the PDF. Please try again.");
            } finally {
                pdfButton.disabled = false;
                pdfButton.textContent = originalText;
                updateSelectionState();
            }
        });
    }

    // =========================================================================
    // INITIAL STATE
    // =========================================================================
    applySettings();
    updateShipmentList();
    updateSelectionState();
});