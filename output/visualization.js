// Main visualization script
(function() {
    'use strict';
    
    let currentCrop = null;
    let currentCountry = null;
    let tradeData = [];
    let animationFrame = 0;
    let animationTimer = null;
    let roughCanvas = null;
    
    // Initialize
    document.addEventListener('DOMContentLoaded', init);
    
    function init() {
        // Check for URL parameters
        const params = new URLSearchParams(window.location.search);
        const urlCrop = params.get('crop');
        const urlCountry = params.get('country');
        
        if (urlCrop && urlCountry) {
            // Direct link - load immediately
            loadDataAndVisualize(urlCrop, urlCountry);
        } else {
            // Show selector
            loadCrops();
            loadCountries();
        }
        
        // Setup event listeners
        document.getElementById('visualize-btn').addEventListener('click', onVisualize);
        document.getElementById('change-btn').addEventListener('click', showSelector);
        document.getElementById('fullscreen-btn').addEventListener('click', toggleFullscreen);
        
        // Initialize Rough.js for handdrawn graphs
        const canvas = document.getElementById('graph-canvas');
        roughCanvas = rough.canvas(canvas);
    }
    
    function loadCrops() {
        // For now, hardcode common crops - will be dynamic after data processing
        const crops = [
            { value: 'wheat', label: 'Wheat' },
            { value: 'rice', label: 'Rice' },
            { value: 'maize', label: 'Maize (Corn)' },
            { value: 'soybeans', label: 'Soybeans' },
            { value: 'barley', label: 'Barley' },
            { value: 'sugar_cane', label: 'Sugar Cane' },
            { value: 'coffee', label: 'Coffee' },
            { value: 'tea', label: 'Tea' }
        ];
        
        const select = document.getElementById('crop-select');
        select.innerHTML = crops.map(crop => 
            `<option value="${crop.value}">${crop.label}</option>`
        ).join('');
    }
    
    function loadCountries() {
        // Load list of available data files and convert to readable names
        const availableCountries = [
            { value: 'aruba', label: 'Aruba' },
            { value: 'australia___new_zealand', label: 'Australia + New Zealand' },
            { value: 'bermuda', label: 'Bermuda' },
            { value: 'bolivia__plurinational_state_of_', label: 'Bolivia (Plurinational State of)' },
            { value: 'c_te_d_ivoire', label: "Côte d'Ivoire" },
            { value: 'china__hong_kong_sar', label: 'China, Hong Kong SAR' },
            { value: 'china__macao_sar', label: 'China, Macao SAR' },
            { value: 'china__mainland', label: 'China, Mainland' },
            { value: 'china__taiwan_province_of', label: 'China, Taiwan Province of' },
            { value: 'czech_republic', label: 'Czech Republic' },
            { value: 'democratic_people_s_republic_of_korea', label: "Democratic People's Republic of Korea" },
            { value: 'eu____ex_int', label: 'EU (ex INT)' },
            { value: 'european_union', label: 'European Union' },
            { value: 'european_union__exc_intra_trade_', label: 'European Union (exc. intra-trade)' },
            { value: 'iran__islamic_republic_of_', label: 'Iran (Islamic Republic of)' },
            { value: 'land_locked_developing_countries', label: 'Land Locked Developing Countries' },
            { value: 'lao_people_s_democratic_republic', label: "Lao People's Democratic Republic" },
            { value: 'least_developed_countries', label: 'Least Developed Countries' },
            { value: 'low_income_food_deficit_countries', label: 'Low Income Food Deficit Countries' },
            { value: 'net_food_importing_developing_countries', label: 'Net Food Importing Developing Countries' },
            { value: 'netherlands', label: 'Netherlands' },
            { value: 'netherlands_antilles', label: 'Netherlands Antilles' },
            { value: 'occupied_palestinian_territory', label: 'Occupied Palestinian Territory' },
            { value: 'small_island_developing_states', label: 'Small Island Developing States' },
            { value: 'sudan__former_', label: 'Sudan (former)' },
            { value: 'swaziland', label: 'Swaziland' },
            { value: 'the_former_yugoslav_republic_of_macedonia', label: 'The former Yugoslav Republic of Macedonia' },
            { value: 'turkey', label: 'Turkey' },
            { value: 'united_kingdom', label: 'United Kingdom' },
            { value: 'venezuela__bolivarian_republic_of_', label: 'Venezuela (Bolivarian Republic of)' }
        ];
        
        // Sort by label
        availableCountries.sort((a, b) => a.label.localeCompare(b.label));
        
        const select = document.getElementById('country-select');
        select.innerHTML = availableCountries.map(country => 
            `<option value="${country.value}">${country.label}</option>`
        ).join('');
        
        // Set default to United Kingdom
        select.value = 'united_kingdom';
        
        document.getElementById('visualize-btn').disabled = false;
    }
    
    function onVisualize() {
        const crop = document.getElementById('crop-select').value;
        const country = document.getElementById('country-select').value;
        
        if (!crop || !country) {
            alert('Please select both crop and country');
            return;
        }
        
        // Update URL without reloading
        const url = new URL(window.location);
        url.searchParams.set('crop', crop);
        url.searchParams.set('country', country);
        window.history.pushState({}, '', url);
        
        loadDataAndVisualize(crop, country);
    }
    
    function loadDataAndVisualize(crop, country) {
        currentCrop = crop;
        currentCountry = country;
        
        document.getElementById('loading-message').style.display = 'block';
        document.getElementById('visualize-btn').disabled = true;
        
        // Try to load data
        const dataPath = `../data/${country}.json`;
        
        fetch(dataPath)
            .then(response => {
                if (!response.ok) throw new Error('Data not found');
                return response.json();
            })
            .then(data => {
                tradeData = data;
                startVisualization();
            })
            .catch(err => {
                console.error('Error loading data:', err);
                alert('Data not available for this combination. Please try another selection.');
                document.getElementById('loading-message').style.display = 'none';
                document.getElementById('visualize-btn').disabled = false;
            });
    }
    
    function startVisualization() {
        // Hide selector
        document.getElementById('selector-overlay').classList.add('hidden');
        
        // Show visualization elements
        document.getElementById('video-container').style.display = 'block';
        document.getElementById('graph-canvas').style.display = 'block';
        document.getElementById('info-overlay').style.display = 'block';
        document.getElementById('controls').style.display = 'block';
        
        // Update info
        document.getElementById('info-crop').textContent = formatCropName(currentCrop);
        document.getElementById('info-country').textContent = formatCountryName(currentCountry);
        
        // Setup canvas
        const canvas = document.getElementById('graph-canvas');
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);
        
        // Calculate max values for scaling
        const maxPrice = Math.max(...tradeData.map(d => d.import_price || 0));
        const maxQuantity = Math.max(...tradeData.map(d => d.import_quantity || 0));
        
        // Start video and animation
        const video = document.getElementById('main-video');
        video.play();
        
        animationFrame = 0;
        const frameInterval = Math.round((54 * 1000) / tradeData.length); // 54 seconds distributed
        
        animationTimer = setInterval(() => {
            updateFrame(animationFrame % tradeData.length, maxPrice, maxQuantity);
            animationFrame++;
        }, frameInterval);
    }
    
    function updateFrame(index, maxPrice, maxQuantity) {
        const data = tradeData[index];
        
        // Update info display
        document.getElementById('info-year').textContent = data.year || '----';
        document.getElementById('info-price').textContent = 
            data.import_price ? data.import_price.toFixed(2) : '----';
        document.getElementById('info-quantity').textContent = 
            data.import_quantity ? Math.round(data.import_quantity).toLocaleString() : '----';
        
        // Update video filter (hue rotate based on price)
        const video = document.getElementById('main-video');
        const hueAngle = Math.round(270 * ((data.import_price || 0) / maxPrice));
        video.style.filter = `hue-rotate(${hueAngle}deg)`;
        
        // Draw graph
        drawGraph(index, maxPrice, maxQuantity);
    }
    
    function drawGraph(currentIndex, maxPrice, maxQuantity) {
        const canvas = document.getElementById('graph-canvas');
        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;
        
        // Clear canvas
        ctx.clearRect(0, 0, width, height);
        
        // Setup dimensions
        const margin = 40;
        const graphWidth = width - margin * 2;
        const graphHeight = height - margin * 2;
        
        // Draw background with rough style
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(margin - 20, margin - 20, graphWidth + 40, graphHeight + 40);
        
        // Draw axes with rough style
        roughCanvas.line(
            margin, margin + graphHeight,
            margin + graphWidth, margin + graphHeight,
            { 
                stroke: '#888', 
                strokeWidth: 2,
                roughness: 1.5,
                bowing: 1
            }
        );
        
        roughCanvas.line(
            margin, margin,
            margin, margin + graphHeight,
            { 
                stroke: '#888', 
                strokeWidth: 2,
                roughness: 1.5,
                bowing: 1
            }
        );
        
        // Draw data line (handdrawn style)
        if (tradeData.length > 1) {
            const points = [];
            
            for (let i = 0; i <= currentIndex && i < tradeData.length; i++) {
                const x = margin + (i / (tradeData.length - 1)) * graphWidth;
                const price = tradeData[i].import_price || 0;
                const y = margin + graphHeight - (price / maxPrice) * graphHeight;
                points.push([x, y]);
            }
            
            // Draw with rough.js for handdrawn effect
            if (points.length > 1) {
                roughCanvas.linearPath(points, {
                    stroke: '#4CAF50',
                    strokeWidth: 3,
                    roughness: 1.2,
                    bowing: 0.5
                });
                
                // Draw points
                points.forEach((point, i) => {
                    if (i === currentIndex) {
                        // Current point - larger and highlighted
                        roughCanvas.circle(point[0], point[1], 12, {
                            stroke: '#4CAF50',
                            strokeWidth: 3,
                            fill: '#4CAF50',
                            fillStyle: 'solid',
                            roughness: 1
                        });
                    } else {
                        // Previous points
                        roughCanvas.circle(point[0], point[1], 6, {
                            stroke: '#4CAF50',
                            strokeWidth: 2,
                            fill: '#2a2a2a',
                            fillStyle: 'solid',
                            roughness: 0.8
                        });
                    }
                });
            }
        }
        
        // Draw labels
        ctx.fillStyle = '#aaa';
        ctx.font = '14px Arial';
        ctx.textAlign = 'center';
        
        // X-axis labels (years)
        const labelInterval = Math.max(1, Math.floor(tradeData.length / 10));
        for (let i = 0; i < tradeData.length; i += labelInterval) {
            const x = margin + (i / (tradeData.length - 1)) * graphWidth;
            ctx.fillText(tradeData[i].year, x, height - 10);
        }
        
        // Y-axis label
        ctx.save();
        ctx.translate(15, height / 2);
        ctx.rotate(-Math.PI / 2);
        ctx.textAlign = 'center';
        ctx.fillText('Import Price (USD/tonne)', 0, 0);
        ctx.restore();
    }
    
    function resizeCanvas() {
        const canvas = document.getElementById('graph-canvas');
        const container = canvas.parentElement;
        
        // Position canvas at bottom
        canvas.style.position = 'fixed';
        canvas.style.bottom = '50px';
        canvas.style.left = '50px';
        canvas.style.right = '50px';
        canvas.style.height = '300px';
        canvas.style.zIndex = '10';
        
        // Set actual canvas dimensions
        const rect = canvas.getBoundingClientRect();
        canvas.width = rect.width;
        canvas.height = rect.height;
    }
    
    function showSelector() {
        // Stop animation
        if (animationTimer) {
            clearInterval(animationTimer);
            animationTimer = null;
        }
        
        // Pause video
        document.getElementById('main-video').pause();
        
        // Hide visualization
        document.getElementById('selector-overlay').classList.remove('hidden');
        document.getElementById('video-container').style.display = 'none';
        document.getElementById('graph-canvas').style.display = 'none';
        document.getElementById('info-overlay').style.display = 'none';
        document.getElementById('controls').style.display = 'none';
    }
    
    function toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    }
    
    function formatCropName(crop) {
        return crop.split('_').map(word => 
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    }
    
    function formatCountryName(country) {
        const countryMap = {
            'aruba': 'Aruba',
            'australia___new_zealand': 'Australia + New Zealand',
            'bermuda': 'Bermuda',
            'bolivia__plurinational_state_of_': 'Bolivia (Plurinational State of)',
            'c_te_d_ivoire': "Côte d'Ivoire",
            'china__hong_kong_sar': 'China, Hong Kong SAR',
            'china__macao_sar': 'China, Macao SAR',
            'china__mainland': 'China, Mainland',
            'china__taiwan_province_of': 'China, Taiwan Province of',
            'czech_republic': 'Czech Republic',
            'democratic_people_s_republic_of_korea': "Democratic People's Republic of Korea",
            'eu____ex_int': 'EU (ex INT)',
            'european_union': 'European Union',
            'european_union__exc_intra_trade_': 'European Union (exc. intra-trade)',
            'iran__islamic_republic_of_': 'Iran (Islamic Republic of)',
            'land_locked_developing_countries': 'Land Locked Developing Countries',
            'lao_people_s_democratic_republic': "Lao People's Democratic Republic",
            'least_developed_countries': 'Least Developed Countries',
            'low_income_food_deficit_countries': 'Low Income Food Deficit Countries',
            'net_food_importing_developing_countries': 'Net Food Importing Developing Countries',
            'netherlands': 'Netherlands',
            'netherlands_antilles': 'Netherlands Antilles',
            'occupied_palestinian_territory': 'Occupied Palestinian Territory',
            'small_island_developing_states': 'Small Island Developing States',
            'sudan__former_': 'Sudan (former)',
            'swaziland': 'Swaziland',
            'the_former_yugoslav_republic_of_macedonia': 'The former Yugoslav Republic of Macedonia',
            'turkey': 'Turkey',
            'united_kingdom': 'United Kingdom',
            'venezuela__bolivarian_republic_of_': 'Venezuela (Bolivarian Republic of)'
        };
        
        return countryMap[country] || country.split('_').map(word => 
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    }
    
})();
