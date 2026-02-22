(async function () {

    // ================================
    // 🔹 GET SYMBOL NAME
    // ================================
    const symbolButton = document.querySelector('button[aria-label="Change symbol"]');

    if (!symbolButton) {
        console.error("Symbol button not found");
        return;
    }

    const symbolName = symbolButton.innerText.trim().toUpperCase();
    console.log("📌 Symbol Detected:", symbolName);

    // ================================
    // 🔹 DETERMINE FILE PREFIX
    // ================================
    let filePrefix = "other";

    if (symbolName.includes("CALL") || symbolName.includes("CE")) {
        filePrefix = "ce";
    } 
    else if (symbolName.includes("PUT") || symbolName.includes("PE")) {
        filePrefix = "pe";
    } 
    else if (
        symbolName.includes("NIFTY") ||
        symbolName.includes("SENSEX") ||
        symbolName.includes("BANKNIFTY") ||
        symbolName.includes("FINNIFTY")
    ) {
        filePrefix = "index";
    }

    console.log("📂 File Type:", filePrefix);

    // ================================
    // 🔹 SCROLL CONTAINER
    // ================================
    const scrollContainer = document.querySelector('.ka-tbody')?.parentElement;

    if (!scrollContainer) {
        console.error("Scroll container not found");
        return;
    }

    let collectedTrades = new Map();
    let reachedTradeOne = false;

    function extractRows() {
        const rows = document.querySelectorAll('.ka-tbody .ka-row');

        rows.forEach(row => {

            const tradeNo = row.querySelector('.tradeNumber-VdWadcSQ')?.innerText?.trim();
            if (!tradeNo) return;

            if (!collectedTrades.has(tradeNo)) {

                const cells = row.querySelectorAll('.ka-cell');

                collectedTrades.set(tradeNo, {
                    symbol: symbolName,
                    tradeNo,
                    direction: row.querySelector('.long-VdWadcSQ') ? "Long" :
                               row.querySelector('.short-VdWadcSQ') ? "Short" : "",
                    type: cells[2]?.innerText.trim(),
                    dateTime: cells[3]?.innerText.trim(),
                    signal: cells[4]?.innerText.trim(),
                    price: cells[5]?.innerText.trim(),
                    positionSize: cells[6]?.innerText.trim(),
                    netPL: cells[7]?.innerText.trim(),
                    cumulativePL: cells[10]?.innerText.trim()
                });

                if (tradeNo === "1") {
                    reachedTradeOne = true;
                }
            }
        });
    }

    console.log("🚀 Starting scroll until Trade #1...");

    while (!reachedTradeOne) {
        extractRows();
        scrollContainer.scrollTop += 800;
        await new Promise(r => setTimeout(r, 400));
    }

    console.log("✅ Reached Trade #1");
    console.log("Total Trades Collected:", collectedTrades.size);

    const result = Array.from(collectedTrades.values())
        .sort((a, b) => Number(a.tradeNo) - Number(b.tradeNo));

    console.log(result);

    // ================================
    // 🔹 DOWNLOAD JSON
    // ================================
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filePrefix}_all_trades.json`;
    a.click();

})();