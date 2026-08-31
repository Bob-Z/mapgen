import gen_road
import config
import math

def generate_road_bots():
    if config.data["road_bots_quantity"] == 0:
        print("No road bots created")
        return None

    road_bots_quantity = min(len(gen_road.get_road_coord()), config.data["road_bots_quantity"])

    script_string = "#include \"base.as\"\n\
\n\
const int truck_qty = " + str(road_bots_quantity) + ";\n\
\n\
int frame_qty = 0;\n\
array<BeamClass@> all_truck(truck_qty);\n\
array<vector3> all_previous_pos(truck_qty);\n\
array<int> all_slow_move_qty(truck_qty);\n\
array<array<vector3>> all_waypoints(truck_qty, array<vector3>(0));\n\
array<string> all_vehicle_name = {"

    for name in config.data["road_bots_name"].split(","):
        script_string = script_string + "\"" + name + "\","

    script_string = script_string[:-1] # remove final ","

    script_string = script_string + "};\n\
bool init_done = false;\n\
\n\
void main()\n\
{\n\
}\n\
\n\
void create_truck(int truck_id)\n\
{\n\
    int x = 0;\n\
    \n\
    // Needed to get the right initial position\n\
    for( uint index = 0; index < 2; index++ )\n\
    {\n\
        game.addWaypoint(all_waypoints[truck_id][index]);\n\
    }\n\
    \n\
    vector3 spawn_pos = all_waypoints[truck_id][0];\n\
    string spawn_sectionconfig = game.getAIVehicleSectionConfig(x);\n\
    string spawn_skin = game.getAIVehicleSkin(x);\n\
    string vehicle_name = all_vehicle_name[truck_id % all_vehicle_name.length()];\n\
    @all_truck[truck_id] = game.spawnTruckAI(vehicle_name, spawn_pos, spawn_sectionconfig, spawn_skin, x);\n\
\n\
    game.clearWaypoints();\n\
\n\
    if (@all_truck[truck_id] == null)\n\
    {\n\
        game.log(\"Vehicle AI: Could not spawn vehicle \'\"+ vehicle_name +\"\',  skipping it...\");\n\
        return;\n\
    }\n\
\n\
    game.log(\"Vehicle \" + all_truck[truck_id].getTruckName() + \" created\");\n\
\n\
    all_previous_pos[truck_id] = all_truck[truck_id].getPosition();\n\
    all_slow_move_qty[truck_id] = 0;\n\
\n\
    VehicleAIClass @current_truck_ai = all_truck[truck_id].getVehicleAI();\n\
\n\
    for( uint index = 0; index < all_waypoints[truck_id].length(); index++ )\n\
    {\n\
        string waypoint_name = \"way\" + formatInt(truck_id) + \".\" + formatInt(index);\n\
        current_truck_ai.addWaypoint(waypoint_name, all_waypoints[truck_id][index]);\n\
		current_truck_ai.setValueAtWaypoint(waypoint_name, AI_SPEED, 30.0);\n\
    }\n\
\n\
    current_truck_ai.setActive(true);\n\
}\n\
\n\
void frameStep(float dt)\n\
{\n\
    if (init_done == false)\n\
    {\n\
        fill_waypoint();\n\
\n\
        for( int truck_id = 0; truck_id < truck_qty; truck_id++ )\n\
        {\n\
            create_truck(truck_id);\n\
        }\n\
\n\
        init_done = true;\n\
    }\n\
\n\
	frame_qty = frame_qty + 1;\n\
\n\
    if (frame_qty % 60 == 0)\n\
    {\n\
        for( int truck_id = 0; truck_id < truck_qty; truck_id++ )\n\
        {\n\
            if (@all_truck[truck_id] != null)\n\
            {\n\
                vector3 pos = all_truck[truck_id].getPosition();\n\
\n\
                float distance = pos.distance(all_previous_pos[truck_id]);\n\
\n\
                if ( distance < 1.0 )\n\
                {\n\
                    all_slow_move_qty[truck_id] = all_slow_move_qty[truck_id] + 1;\n\
				    if ( all_slow_move_qty[truck_id] > " \
                    + str(int(config.data["bots_slow_move_timeout_before_reset"])) + ")\n\
			    	    {\n\
                        int instance_id = all_truck[truck_id].getInstanceId();\n\
                        game.log(\"reset AI vehicle \" + formatInt(instance_id));\n\
                        all_slow_move_qty[truck_id] = 0;\n\
\n\
                        game.pushMessage(MSG_SIM_DELETE_ACTOR_REQUESTED, {  {\"instance_id\",instance_id} });\n\
\n\
                        create_truck(truck_id);\n\
                    }\n\
                }\n\
                else\n\
                {\n\
                    all_slow_move_qty[truck_id] = 0;\n\
                }\n\
\n\
                all_previous_pos[truck_id] = pos;\n\
            }\n\
        }\n\
    }\n\
}\n\
\n\
void fill_waypoint()\n\
{\n"

    all_road = gen_road.get_road_coord()
    road_created_qty = 0

    for road_data in all_road:
        script_string = script_string + "       all_waypoints[" + str(road_created_qty) + "].resize(" + str(
            len(road_data)) + ");\n"

        index = 0
        for data in road_data:
            split_data = data.split(", ")
            script_string = script_string + "       all_waypoints[" + str(road_created_qty) + "][" + str(index) + \
                            "] = vector3(" + split_data[0] + ",0," + split_data[2] + ");\n"
            index += 1
        road_created_qty += 1

        if config.data["road_bots_quantity"] == road_created_qty:
            break
        script_string = script_string + "\n"

    script_string = script_string + "}"

    print(str(road_created_qty) + " road bots created\n")
    return script_string
