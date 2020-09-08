package com.example.albertalarm;

import android.os.Bundle;
import androidx.appcompat.app.AppCompatActivity;

import com.daimajia.swipe.SwipeLayout;


public class BusActivity extends AppCompatActivity {

    private SwipeLayout busEdit;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_bus);

        busEdit = (SwipeLayout)findViewById(R.id.edit_bus);

        busEdit.setShowMode(SwipeLayout.ShowMode.LayDown);
        busEdit.addDrag(SwipeLayout.DragEdge.Right,busEdit.findViewWithTag("HideTag"));
    }

}
