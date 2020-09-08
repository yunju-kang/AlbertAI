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

    TextView example;
    Button btnTraffic;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);



        example = (TextView)findViewById(R.id.Example);
        btnTraffic = (Button)findViewById(R.id.btnTraffic);

        example.setOnTouchListener(new OnSwipeTouchListener(MainActivity.this){
            @Override
            public void onSwipeRight() {
                Toast.makeText(MainActivity.this, "right", Toast.LENGTH_SHORT).show();

            }
            public void onSwipeLeft(){
                Toast.makeText(MainActivity.this, "left", Toast.LENGTH_SHORT).show();
            }
        });

        btnTraffic.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent busIntent = new Intent(view.getContext(), BusActivity.class);
                startActivityForResult(busIntent, 0);
            }
        });



    }


}