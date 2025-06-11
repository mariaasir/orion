/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { mount } from "@odoo/owl";

class ChatComponent extends Component {
    setup() {
        this.state = useState({
            messages: [],
            newMessage: ""
        });

        onWillStart(async () => {
            // Simula carga inicial
            this.state.messages = [
                { sender: "Parent", body: "Hello, how much is the  activity of Sunday?" },
                { sender: "Monitor", body: "20 euros. " }
            ];
        });
    }

    sendMessage() {
        if (this.state.newMessage.trim()) {
            this.state.messages.push({
                sender: "Yo",
                body: this.state.newMessage
            });
            this.state.newMessage = "";
        }
    }
}

ChatComponent.template = "orion_chatter_management.ChatComponent";

mount(ChatComponent, document.getElementById("chat_component"));
