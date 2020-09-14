package com.example.albertalarm;

import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;

import androidx.appcompat.app.AppCompatActivity;
import androidx.drawerlayout.widget.DrawerLayout;


public class BusActivity extends AppCompatActivity {

    //Button btnOpen;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_bus);

        //btnOpen = (Button)findViewById(R.id.open);


        // open DrawerLayout Event
       /* btnOpen.setOnClickListener(new Button.OnClickListener(){
            @Override
            public void onClick(View v){
                DrawerLayout layDrawer = (DrawerLayout)findViewById(R.id.drawer);
                if(!layDrawer.isDrawerOpen(Gravity.LEFT)){
                    layDrawer.openDrawer(Gravity.LEFT);
                }
            }
        });  */


    }

}
