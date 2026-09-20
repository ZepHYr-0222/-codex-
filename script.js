// 全局数据存储
let rawData = [];
let cleanData = [];

// DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    const fetchBtn = document.getElementById('fetchBtn');
    const processBtn = document.getElementById('processBtn');
    const stockInput = document.getElementById('stockCode');
    const statusMessage = document.getElementById('statusMessage');

    // 显示状态消息
    function showStatus(message, type) {
        statusMessage.textContent = message;
        statusMessage.className = 'status-message ' + type;
    }

    // 隐藏状态消息
    function hideStatus() {
        statusMessage.className = 'status-message';
    }

    // 设置按钮状态
    function setButtonsDisabled(disabled) {
        fetchBtn.disabled = disabled;
        processBtn.disabled = disabled;
    }

    // 验证股票代码格式
    function validateStockCode(code) {
        if (!code || code.trim() === '') {
            return false;
        }
        // A股代码：6位数字（沪市600/601/603/688开头，深市000/001/002/003/300开头）
        const pattern = /^[0-9]{6}$/;
        return pattern.test(code.trim());
    }

    // 抓取数据
    fetchBtn.addEventListener('click', async function() {
        const stockCode = stockInput.value.trim();

        if (!validateStockCode(stockCode)) {
            showStatus('请输入有效的6位股票代码（如：000001、600519）', 'error');
            return;
        }

        setButtonsDisabled(true);
        showStatus('正在通过Playwright抓取 ' + stockCode + ' 的历史分红数据，请稍候...', 'info');

        try {
            const response = await fetch('http://127.0.0.1:5000/api/fetch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ stock_code: stockCode })
            });

            if (!response.ok) {
                throw new Error('服务器响应错误: ' + response.status);
            }

            const result = await response.json();

            if (result.rawData && result.rawData.length > 0) {
                rawData = result.rawData;
                renderRawTable();
                showStatus('成功抓取 ' + rawData.length + ' 条分红记录', 'success');
                updateStats();
            } else {
                showStatus('未获取到分红数据，请检查股票代码是否正确', 'error');
            }
        } catch (error) {
            console.error('抓取失败:', error);
            showStatus('数据抓取失败：' + error.message + '（请确认后端服务已启动）', 'error');
        } finally {
            setButtonsDisabled(false);
        }
    });

    // 数据预处理
    processBtn.addEventListener('click', async function() {
        if (rawData.length === 0) {
            showStatus('请先抓取数据，再进行预处理', 'error');
            return;
        }

        setButtonsDisabled(true);
        showStatus('正在进行数据预处理...', 'info');

        try {
            const res = await fetch('http://127.0.0.1:5000/api/preprocess',{
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ data: rawData })
            });

            if (!res.ok) { // ✅修改为 res.ok
                throw new Error('服务器响应错误: ' + res.status);
            }

            const result = await res.json();

            if (result.success) {
                cleanData = result.data;
                renderCleanTable();
                showStatus('数据预处理完成，共 ' + cleanData.length + ' 条清洗后记录', 'success');
                updateStats();
            } else {
                showStatus('数据预处理失败', 'error');
            }
        } catch (error) {
            console.error('预处理失败:', error);
            showStatus('数据预处理失败：' + error.message, 'error');
        } finally {
            setButtonsDisabled(false);
        }
    });



    // 渲染原始数据表格
    function renderRawTable() {
        const tbody = document.querySelector('#rawTable tbody');
        const stockCode = document.getElementById('stockCode').value.trim();

        if (rawData.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="empty-data">暂无数据</td></tr>';
            return;
        }

        tbody.innerHTML = rawData.map(item => {
            const songZhuan = (parseFloat(item['送股(股)'] || 0) + parseFloat(item['转增(股)'] || 0)) / 10;
            const paiXi = parseFloat(item['派息(税前)(元)'] || 0) / 10;
            let year = '-';
            if(item['公告日期']){
                year = item['公告日期'].substring(0,4);
            }
            return '<tr>' +
                '<td>' + stockCode + '</td>' +
                '<td>' + year + '</td>' +
                '<td>送股:' + (item['送股(股)']||0) + ',转增:' + (item['转增(股)']||0) + ',派息:' + (item['派息(税前)(元)']||0) + '</td>' +
                '<td>' + songZhuan.toFixed(4) + '</td>' +
                '<td>' + paiXi.toFixed(4) + '</td>' +
                '<td>' + (item['股权登记日'] || '--') + '</td>' +
                '<td>' + (item['除权除息日'] || '--') + '</td>' +
            '</tr>';
        }).join('');
    }
    // 渲染清洗后的数据表格
    function renderCleanTable() {
        const tbody = document.querySelector('#cleanTable tbody');
        const stockCode = document.getElementById('stockCode').value.trim();

        if (cleanData.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" class="empty-data">暂无数据</td></tr>';
            return;
        }

        tbody.innerHTML = cleanData.map(item => {
            let year = '-';
            if(item['公告日期']){
                year = String(item['公告日期']).substring(0,4);
            }
            const plan = `送股:${item['送股(股)']||0},转增:${item['转增(股)']||0},派息:${item['派息(税前)(元)']||0}`;
            const songZhuan = parseFloat(item['shares_distribution'] || 0).toFixed(4);
            const paiXi = parseFloat(item['dividend_per_share'] || 0).toFixed(4);
            const registerDate = item['股权登记日'] || '--';
            const exDate = item['除权除息日'] || '--';
            const rate = parseFloat(item['dividend_rate'] || 0).toFixed(2);

            return '<tr>' +
                '<td>' + stockCode + '</td>' +
                '<td>' + year + '</td>' +
                '<td>' + plan + '</td>' +
                '<td>' + songZhuan + '</td>' +
                '<td>' + paiXi + '</td>' +
                '<td>' + registerDate + '</td>' +
                '<td>' + exDate + '</td>' +
                '<td>' + rate + '</td>' +
            '</tr>';
        }).join('');
        updateStats();
    }





    // 更新统计信息
    function updateStats() {
        document.getElementById('totalRecords').textContent = rawData.length;
        document.getElementById('cleanRecords').textContent = cleanData.length;

        if (cleanData.length > 0) {
            const avgDividend = cleanData.reduce((sum, item) => {
                return sum + (parseFloat(item.dividend_per_share) || 0);
            }, 0) / cleanData.length;
            document.getElementById('avgDividend').textContent = avgDividend.toFixed(4);

            const avgRate = cleanData.reduce((sum, item) => {
                return sum + (parseFloat(item.dividend_rate) || 0);
            }, 0) / cleanData.length;
            document.getElementById('avgRate').textContent = avgRate.toFixed(2) + '%';
        } else {
            document.getElementById('avgDividend').textContent = '0.00';
            document.getElementById('avgRate').textContent = '0.00%';
        }
    }

    // 支持回车键抓取
    stockInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            fetchBtn.click();
        }
    });
});
