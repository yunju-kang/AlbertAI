package com.example.albertalarm;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.daimajia.swipe.SwipeLayout;


public class MainActivity extends AppCompatActivity {

    Button btnTraffic, btnReminder, btnAlarm;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);


        btnTraffic = (Button)findViewById(R.id.btnTraffic);
        btnReminder = (Button)findViewById(R.id.btnReminder);
        btnAlarm = (Button)findViewById(R.id.btnAlarm);

//        example.setOnTouchListener(new OnSwipeTouchListener(MainActivity.this){
//            @Override
//            public void onSwipeRight() {
//                Toast.makeText(MainActivity.this, "right", Toast.LENGTH_SHORT).show();
//
//            }
//            public void onSwipeLeft(){
//                Toast.makeText(MainActivity.this, "left", Toast.LENGTH_SHORT).show();
//            }
//        });


        // move Traffic layout
        btnTraffic.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent busIntent = new Intent(view.getContext(), BusActivity.class);
                startActivityForResult(busIntent, 0);
            }
        });

        // move Reminder layout
        btnReminder.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent busIntent = new Intent(view.getContext(), BusActivity.class);
                startActivityForResult(busIntent, 0);
            }
        });

        // move Alarm layout
        btnAlarm.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent busIntent = new Intent(view.getContext(), BusActivity.class);
                startActivityForResult(busIntent, 0);
            }
        });



    }


}