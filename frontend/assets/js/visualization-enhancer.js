// Enhanced Dynamic Visualization Utilities
// Makes ALL charts responsive, interactive, and data-driven

window.VisualizationEnhancer = {
    // Default layout for all charts - fits properly
    getResponsiveLayout(title, customLayout = {}) {
        return {
            title: {
                text: title,
                font: { size: 16, family: 'Inter, sans-serif', weight: 600 }
            },
            autosize: true,
            height: 450,
            margin: { l: 60, r: 40, t: 60, b: 60 },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: { family: 'Inter, sans-serif', size: 12 },
            hoverlabel: {
                bgcolor: 'white',
                font: { size: 13 },
                bordercolor: '#0066cc'
            },
            ...customLayout
        };
    },

    // Interactive config for all charts
    getInteractiveConfig() {
        return {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['lasso2d', 'select2d'],
            modeBarButtonsToAdd: ['hoverclosest', 'hovercompare']
        };
    },

    // Create dynamic bar chart that updates with data
    createDynamicBarChart(elementId, data, title, xLabel, yLabel) {
        const trace = {
            x: data.map(d => d.x),
            y: data.map(d => d.y),
            type: 'bar',
            marker: {
                color: data.map(d => d.y),
                colorscale: 'Viridis',
                showscale: true,
                line: { width: 1, color: 'white' }
            },
            text: data.map(d => d.y.toFixed(3)),
            textposition: 'outside',
            hovertemplate: `<b>${xLabel}:</b> %{x}<br><b>${yLabel}:</b> %{y:.3f}<extra></extra>`
        };

        const layout = this.getResponsiveLayout(title, {
            xaxis: { title: xLabel, tickangle: -45 },
            yaxis: { title: yLabel, gridcolor: 'rgba(128,128,128,0.2)' },
            bargap: 0.15
        });

        Plotly.newPlot(elementId, [trace], layout, this.getInteractiveConfig());
        
        // Make chart resize with window
        window.addEventListener('resize', () => {
            Plotly.Plots.resize(elementId);
        });
    },

    // Create animated scatter plot
    createAnimatedScatter(elementId, data, title, xLabel, yLabel, colorBy) {
        const trace = {
            x: data.map(d => d.x),
            y: data.map(d => d.y),
            mode: 'markers',
            type: 'scatter',
            marker: {
                size: data.map(d => d.size || 10),
                color: data.map(d => d.color || d.y),
                colorscale: 'Portland',
                showscale: true,
                colorbar: { title: colorBy },
                line: { width: 2, color: 'white' }
            },
            text: data.map(d => d.label || ''),
            hovertemplate: `<b>%{text}</b><br>${xLabel}: %{x:.3f}<br>${yLabel}: %{y:.3f}<extra></extra>`
        };

        const layout = this.getResponsiveLayout(title, {
            xaxis: { title: xLabel, gridcolor: 'rgba(128,128,128,0.2)' },
            yaxis: { title: yLabel, gridcolor: 'rgba(128,128,128,0.2)' },
            hovermode: 'closest'
        });

        Plotly.newPlot(elementId, [trace], layout, this.getInteractiveConfig());
        
        window.addEventListener('resize', () => {
            Plotly.Plots.resize(elementId);
        });
    },

    // Create 3D surface plot for multi-dimensional data
    create3DSurface(elementId, data, title, xLabel, yLabel, zLabel) {
        const trace = {
            z: data.z,
            x: data.x,
            y: data.y,
            type: 'surface',
            colorscale: 'Jet',
            contours: {
                z: {
                    show: true,
                    usecolormap: true,
                    highlightcolor: "#42f462",
                    project: { z: true }
                }
            }
        };

        const layout = this.getResponsiveLayout(title, {
            scene: {
                xaxis: { title: xLabel },
                yaxis: { title: yLabel },
                zaxis: { title: zLabel },
                camera: {
                    eye: { x: 1.87, y: 0.88, z: -0.64 }
                }
            },
            height: 600
        });

        Plotly.newPlot(elementId, [trace], layout, this.getInteractiveConfig());
        
        window.addEventListener('resize', () => {
            Plotly.Plots.resize(elementId);
        });
    },

    // Create sunburst chart for hierarchical data
    createSunburst(elementId, data, title) {
        const trace = {
            type: 'sunburst',
            labels: data.labels,
            parents: data.parents,
            values: data.values,
            branchvalues: 'total',
            marker: {
                colorscale: 'Blues',
                cmid: 0
            },
            hovertemplate: '<b>%{label}</b><br>Value: %{value}<br>%{percentParent}<extra></extra>'
        };

        const layout = this.getResponsiveLayout(title, {
            height: 500
        });

        Plotly.newPlot(elementId, [trace], layout, this.getInteractiveConfig());
        
        window.addEventListener('resize', () => {
            Plotly.Plots.resize(elementId);
        });
    },

    // Create parallel coordinates plot
    createParallelCoordinates(elementId, data, title, dimensions) {
        const trace = {
            type: 'parcoords',
            line: {
                color: data.colors || data.values[0],
                colorscale: 'Jet',
                showscale: true,
                cmin: 0,
                cmax: 1
            },
            dimensions: dimensions.map(dim => ({
                label: dim.label,
                values: dim.values,
                range: dim.range || [Math.min(...dim.values), Math.max(...dim.values)]
            }))
        };

        const layout = this.getResponsiveLayout(title, {
            height: 500,
            margin: { l: 100, r: 100, t: 60, b: 60 }
        });

        Plotly.newPlot(elementId, [trace], layout, this.getInteractiveConfig());
        
        window.addEventListener('resize', () => {
            Plotly.Plots.resize(elementId);
        });
    },

    // Create radar chart for multi-metric comparison
    createRadarChart(elementId, data, title) {
        const traces = data.map(series => ({
            type: 'scatterpolar',
            r: series.values,
            theta: series.labels,
            fill: 'toself',
            name: series.name,
            marker: { size: 6 },
            line: { width: 2 }
        }));

        const layout = this.getResponsiveLayout(title, {
            polar: {
                radialaxis: {
                    visible: true,
                    range: [0, 1],
                    gridcolor: 'rgba(128,128,128,0.3)'
                }
            },
            showlegend: true,
            height: 500
        });

        Plotly.newPlot(elementId, traces, layout, this.getInteractiveConfig());
        
        window.addEventListener('resize', () => {
            Plotly.Plots.resize(elementId);
        });
    },

    // Create sankey diagram for flow visualization
    createSankeyDiagram(elementId, data, title) {
        const trace = {
            type: 'sankey',
            orientation: 'h',
            node: {
                pad: 15,
                thickness: 20,
                line: {
                    color: 'black',
                    width: 0.5
                },
                label: data.nodes,
                color: data.nodeColors || 'blue'
            },
            link: {
                source: data.sources,
                target: data.targets,
                value: data.values,
                color: 'rgba(0,0,255,0.3)'
            }
        };

        const layout = this.getResponsiveLayout(title, {
            height: 500
        });

        Plotly.newPlot(elementId, [trace], layout, this.getInteractiveConfig());
        
        window.addEventListener('resize', () => {
            Plotly.Plots.resize(elementId);
        });
    },

    // Create heatmap with annotations
    createHeatmap(elementId, data, title, xLabels, yLabels) {
        const trace = {
            z: data,
            x: xLabels,
            y: yLabels,
            type: 'heatmap',
            colorscale: 'RdYlGn',
            hovertemplate: 'X: %{x}<br>Y: %{y}<br>Value: %{z:.3f}<extra></extra>',
            showscale: true
        };

        const layout = this.getResponsiveLayout(title, {
            xaxis: { side: 'bottom' },
            yaxis: { autorange: 'reversed' },
            height: 500
        });

        Plotly.newPlot(elementId, [trace], layout, this.getInteractiveConfig());
        
        window.addEventListener('resize', () => {
            Plotly.Plots.resize(elementId);
        });
    }
};

// Make it globally available
window.vizEnhancer = window.VisualizationEnhancer;

