(async function () {

    // ================================
    // 🔹 GET SYMBOL NAME
    // ================================
    const symbolButton = document.querySelector('button.title-l31H9iuA');

    if (!symbolButton) {
        console.error("Symbol button not found");
        return;
    }

    const symbolName = symbolButton.innerText.trim();
    console.log("📌 Symbol Detected:", symbolName);

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
                    symbol: symbolName,   // ✅ ADDED HERE
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

    // ================================
    // 🔹 DOWNLOAD JSON
    // ================================
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = symbolName.replace(/\s+/g, "_") + '_all_trades.json';
    a.click();

})();