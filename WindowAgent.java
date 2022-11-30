import jade.core.AID;
import jade.core.Agent;

public class WindowAgent extends Agent {
    protected void setup() {
        // Printout a welcome message
        System.out.println("Hallo! Buyer-agent "+getAID().getName()+" is ready.");

        String nickname = "Peter";
        AID id = new AID(nickname, AID.ISLOCALNAME);
    }
}

