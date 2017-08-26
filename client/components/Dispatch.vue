<template>
  <div class="dispatch-modal">
    <button @click="$emit('reject')" style="float: right">X</button>
    <h1>{{vehicle.registrationno}}</h1>
    <h2>{{vehicle.status.crew}}</h2>
    <h3>Currently at: {{vehicle.location}}</h3>
    <h3>Busy until: {{vehicle.status.busyUntil}} <BusyStatus :value="vehicle.status.busyUntil" style="display: inline-block"/></h3>
    <div class="columns">
      <div>
        Origin:
        <DatasheetCell>
          <div v-if="originDescription">
            {{originDescription}}
          </div>
          <div v-else class="blank-location">
            (Origin address)
          </div>
          <OnemapAutocomplete class="the-editor"
            :text="originDescription"
            @place_changed="updateGeo('origin', $event)"
            slot="editor"/>
        </DatasheetCell>
        <textarea v-model="originExtra" class="full-width"
          placeholder="e.g. #01-10, Ward 10, Bed 6"/>
      </div>
      <div>
        Destination:
        <DatasheetCell>
          <div v-if="destinationDescription">
            {{destinationDescription}}
          </div>
          <div v-else class="blank-location">
            (Destination address)
          </div>
          <OnemapAutocomplete class="the-editor"
            :text="destinationDescription"
            @place_changed="updateGeo('destination', $event)"
            slot="editor"/>
        </DatasheetCell>
        <textarea v-model="destinationExtra" class="full-width"
          placeholder="e.g. #01-10, Ward 10, Bed 6"/>
      </div>
    </div>
    <div>
      This case ends at:
      <div class="future-time-input-group">
        <button @click="busyUntil = addTime(-30 * 60e3)">-30</button>
        <button @click="busyUntil = addTime(-10 * 60e3)">-10</button>
        <FutureTimeInput v-model="busyUntil" placeholder="18:00" @input.native="timeDirty = true" />
        <button @click="busyUntil = addTime(+10 * 60e3)">+10</button>
        <button @click="busyUntil = addTime(+30 * 60e3)">+30</button>
      </div>
      <HumanizedDuration :duration="busyUntil ? busyUntil - now : null" />
      <br/>
      <br/>
    </div>
    <div>
      Details:
      <textarea v-model="details" class="full-width"
        placeholder="e.g. SoB, needs oxygen, family members"/>
    </div>

    <div class="button-row">
      <button @click="returnDispatch">OK</button>
      <button @click="$emit('reject')">Cancel</button>
    </div>
  </div>
</template>
<style lang="scss">
.dispatch-modal {
  textarea {
    font-family: sans-serif;
    border: solid 1px #CCC;
    min-height: 4em;
  }
}
.columns {
  display: flex;
  flex-direction: row;

  & > * {
    padding: 0 1em;
    flex: 0 1 300px;
  }

  .onemap-autocomplete {
    display: flex;
    flex: 1 1 auto;
    input {
      position: absolute;
      width: 100%; height: 100%;
      left: 0; top: 0;
    }
  }
}
.button-row {
  text-align: center;
  button {
    min-width: 10em;
    padding: 0.5em;
    font-weight: bold;
    margin: 0 0.5em;
  }
}
.blank-location {
  font-style: italic;
  color: #CCC;
}
.future-time-input-group {
  button, input {
    height: 2.4em;
    font-size: 120%;
    text-align: center;
  }
}
</style>
<script>
import OnemapAutocomplete from '~/components/OnemapAutocomplete'
import DatasheetCell from '~/components/DatasheetCell'
import BusyStatus from '~/components/BusyStatus'
import FutureTimeInput from '~/components/FutureTimeInput'
import HumanizedDuration from '~/components/HumanizedDuration'
import {pick} from 'lodash'
import {latlngDistance} from '~/util/geo'

export default {
  components: {OnemapAutocomplete, BusyStatus, DatasheetCell, HumanizedDuration, FutureTimeInput},
  props: ['resolve', 'reject', 'vehicle', 'originPlace'],
  data () {
    return {
      originDescription: '',
      origin: null,
      originExtra: '',

      destinationDescription: '',
      destinationExtra: '',
      destination: null,
      details: '',
      busyUntil: null,

      timeDirty: false,
      now: Date.now()
    }
  },
  created () {
    this.$nowInterval = setInterval(() => { this.now = Date.now() }, 60000)
  },
  destroyed () {
    clearInterval(this.$nowInterval)
  },
  computed: {
    estimatedTime () {
      if (this.origin && this.destination) {
        const totalDistance = latlngDistance(
          [parseFloat(this.vehicle.latitude), parseFloat(this.vehicle.longitude)],
          [this.origin.lat, this.origin.lng]
        ) + latlngDistance(
            [this.origin.lat, this.origin.lng],
            [this.destination.lat, this.destination.lng]
          )
        return (totalDistance / 1000 / 50 * 3600e3) + 20 * 60e3
      } else {
        return null
      }
    }
  },
  watch: {
    estimatedTime (est) {
      if (!this.timeDirty && est !== null) {
        this.busyUntil = new Date(Date.now() + est)
      }
    },
    originPlace: {
      immediate: true,
      handler (p) {
        if (p) {
          this.originDescription = p.result.ADDRESS
          this.origin = p.location
        }
      },
    }
  },
  methods: {
    updateGeo (which, r) {
      this[which + 'Description'] = r.result.ADDRESS
      this[which] = r.location
    },

    returnDispatch () {
      this.$emit(
        'resolve',
        [
          this.vehicle.registrationno,
          {
            ...pick(this, [
              'origin',
              'originDescription',
              'originExtra',
              'destination',
              'destinationDescription',
              'destinationExtra',
              'details',
            ]),
            busyUntil: this.busyUntil ? new Date(this.busyUntil) : null,
          }
        ]
      )
    },
    addTime (t) {
      this.timeDirty = true
      return new Date(Math.max(
        Date.now(),
        (this.busyUntil ? this.busyUntil.getTime() : Date.now()) + t
      ))
    }
  },
}
</script>
