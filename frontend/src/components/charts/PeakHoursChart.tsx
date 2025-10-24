'use client'

import { useEffect, useRef } from 'react'
import Highcharts from 'highcharts'
import HighchartsReact from 'highcharts-react-official'
import { useTheme } from '@/contexts/ThemeContext'
import { getDarkModeChartOptions } from '@/lib/highcharts-config'

interface PeakHoursChartProps {
  data: Array<{ hour: number; sales: number; count: number }>
}

export default function PeakHoursChart({ data }: PeakHoursChartProps) {
  const { isDarkMode } = useTheme()
  const chartRef = useRef<HighchartsReact.RefObject>(null)

  useEffect(() => {
    // SVG path animation from your code
    const animateSVGPath = (svgElem: any, animation: any, callback?: () => void) => {
      const length = svgElem.element.getTotalLength()
      svgElem.attr({
        'stroke-dasharray': length,
        'stroke-dashoffset': length,
        opacity: 1
      })
      svgElem.animate({
        'stroke-dashoffset': 0
      }, animation, callback)
    }

    Highcharts.seriesTypes.line.prototype.animate = function (init) {
      const series = this
      const animation = Highcharts.animObject(series.options.animation)
      if (!init && series.graph) {
        animateSVGPath(series.graph, animation)
      }
    }

    // Axis animation
    Highcharts.addEvent(Highcharts.Axis, 'afterRender', function () {
      const axis = this
      const chart = axis.chart
      const animation = Highcharts.animObject(chart.renderer.globalAnimation)

      if (axis.axisGroup) {
        axis.axisGroup
          .attr({
            opacity: 0,
            rotation: -3,
            scaleY: 0.9
          })
          .animate({
            opacity: 1,
            rotation: 0,
            scaleY: 1
          }, animation)
      }

      if (axis.horiz && axis.labelGroup) {
        axis.labelGroup
          .attr({
            opacity: 0,
            rotation: 3,
            scaleY: 0.5
          })
          .animate({
            opacity: 1,
            rotation: 0,
            scaleY: 1
          }, animation)
      } else if (axis.labelGroup) {
        axis.labelGroup
          .attr({
            opacity: 0,
            rotation: 3,
            scaleX: -0.5
          })
          .animate({
            opacity: 1,
            rotation: 0,
            scaleX: 1
          }, animation)
      }

      // Plot lines animation
      if (axis.plotLinesAndBands) {
        axis.plotLinesAndBands.forEach((plotLine: any) => {
          const animation = Highcharts.animObject(plotLine.options.animation)

          if (plotLine.label) {
            plotLine.label.attr({ opacity: 0 })
          }

          if (plotLine.svgElem) {
            animateSVGPath(plotLine.svgElem, animation, function () {
              if (plotLine.label) {
                plotLine.label.animate({ opacity: 1 })
              }
            })
          }
        })
      }
    })
  }, [])

  const options: Highcharts.Options = {
    ...getDarkModeChartOptions(isDarkMode),
    chart: {
      type: 'line',
      backgroundColor: 'transparent',
      animation: {
        duration: 1000,
        easing: (t: number) => t
      }
    },
    title: {
      text: 'Peak Sales Hours',
      align: 'left',
      style: {
        color: isDarkMode ? '#f3f4f6' : '#1f2937'
      }
    },
    xAxis: {
      title: {
        text: 'Hour of Day',
        style: {
          color: isDarkMode ? '#f3f4f6' : '#1f2937'
        }
      },
      categories: data.map(d => `${d.hour}:00`),
      lineColor: isDarkMode ? '#374151' : '#e5e7eb',
      labels: {
        style: {
          color: isDarkMode ? '#9ca3af' : '#666'
        }
      }
    },
    yAxis: {
      title: {
        text: 'Sales Amount (₹)',
        style: {
          color: isDarkMode ? '#f3f4f6' : '#1f2937'
        }
      },
      gridLineColor: isDarkMode ? '#374151' : '#e5e7eb',
      labels: {
        style: {
          color: isDarkMode ? '#9ca3af' : '#666'
        }
      }
    },
    credits: {
      enabled: false
    },
    tooltip: {
      split: true,
      crosshairs: true,
      backgroundColor: isDarkMode ? '#1f2937' : '#ffffff',
      borderColor: isDarkMode ? '#374151' : '#e5e7eb',
      style: {
        color: isDarkMode ? '#f3f4f6' : '#1f2937'
      }
    },
    plotOptions: {
      line: {
        animation: false,
        marker: {
          enabled: false
        }
      }
    },
    series: [{
      type: 'line',
      name: 'Sales',
      data: data.map(d => d.sales)
    }],
    responsive: {
      rules: [{
        condition: {
          maxWidth: 500
        },
        chartOptions: {
          yAxis: {
            labels: {
              align: 'left',
              x: 0,
              y: -3
            },
            tickLength: 0,
            title: {
              align: 'high',
              reserveSpace: false,
              rotation: 0,
              textAlign: 'left',
              y: -20
            }
          }
        }
      }]
    }
  }

  return (
    <div className="w-full">
      <HighchartsReact highcharts={Highcharts} options={options} ref={chartRef} />
    </div>
  )
}
