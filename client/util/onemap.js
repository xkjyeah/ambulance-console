
export function resultToPlace (r) {
  return {
    location: {
      lat: parseFloat(r.LATITUDE),
      lng: parseFloat(r.LONGITUDE),
    },
    description: r.ADDRESS,
    result: r
  }
}
