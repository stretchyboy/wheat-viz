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
        // Load from existing countries list
        fetch('../countries.txt')
            .then(response => response.text())
            .then(text => {
                const countries = text.split('\n')
                    .filter(c => c.trim())
                    .sort();
                
                const select = document.getElementById('country-select');
                select.innerHTML = countries.map(country => {
                    const value = country.toLowerCase().replace(/[^a-z0-9]+/g, '_');
                    return `<option value="${value}">${country}</option>`;
                }).join('');
                
                // Set default to United Kingdom
                select.value = 'united_kingdom';
                
                document.getElementById('visualize-btn').disabled = false;
            })
            .catch(err => {
                console.error('Error loading countries:', err);
                // Fallback to basic list
                document.getElementById('country-select').innerHTML = 
                    '<option value="world">World</option>' +
                    '<option value="united_kingdom">United Kingdom</option>' +
                    '<option value="united_states_of_america">United States</option>';
                document.getElementById('visualize-btn').disabled = false;
            });
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
        return country.split('_').map(word => 
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    }
    
})();
