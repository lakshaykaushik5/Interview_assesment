/// <reference lib="webworker" />

class AudioProcessor extends AudioWorkletProcessor{

    process(inputs,outputs,parameters){
        const input = inputs[0]
        const channel = input[0]

        if(!channel){
            return true
        }

        this.port.postMessage(channel)

        return true

    }
}

registerProcessor('audio-processor-worker',AudioProcessor)