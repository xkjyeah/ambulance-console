import icon from './ambulanceIcon.png'

const WIDTH = 70
const HEIGHT = 70
const canvas = typeof document !== 'undefined' && document.createElement('canvas')
if (canvas) {
  canvas.width = WIDTH
  canvas.height = HEIGHT
}

export class RotatedImage {
  constructor (imgSource) {
    this.loaded = false
    this.image = new Image()
    this.image.src = imgSource
    this.imageLoadPromise = new Promise((resolve) => {
      this.image.onload = resolve
    })
      .then(() => {
        this.loaded = true
      })
  }

  rotate (radians, overlayText) {
    if (!this.loaded) {
      return null
    }

    const ctx = canvas.getContext('2d')
    ctx.setTransform(1, 0, 0, 1, 0, 0)
    // resetTransform not working in safari
    // ctx.resetTransform()
    ctx.clearRect(0, 0, WIDTH, HEIGHT)

    ctx.translate(WIDTH / 2, HEIGHT / 2)
    ctx.rotate(radians)
    ctx.translate(-WIDTH / 2, -HEIGHT / 2)

    ctx.drawImage(this.image, 0, 0, WIDTH, HEIGHT)

    if (overlayText) {
      ctx.setTransform(1, 0, 0, 1, 0, 0)
      ctx.font = 'bold 12px sans-serif'
      ctx.fillStyle = 'black'
      ctx.strokeStyle = 'white'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'

      ctx.strokeText(overlayText + '', WIDTH / 2, HEIGHT - 12)
      ctx.fillText(overlayText + '', WIDTH / 2, HEIGHT - 12)
      // ctx.rotate(Math.PI)
    }

    return canvas.toDataURL()
  }
}

const image = typeof document !== 'undefined' && new RotatedImage(icon)
// const cache = new Array(8)

export default function getImage (direction, overlay) {
  // cache[direction] = cache[direction] || image.rotate(direction * Math.PI / 4, overlay)
  return image.rotate((-direction + 1) * Math.PI / 4, overlay)
  // return {
  //   url: image.rotate((-direction + 1) * Math.PI / 4, overlay),
  //   anchor: typeof google !== 'undefined' ? new google.maps.Point(35, 35) : null,
  // }
  // return cache[direction]
}
